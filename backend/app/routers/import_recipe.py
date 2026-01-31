import json
import logging
import uuid
from pathlib import Path

import httpx
from bs4 import BeautifulSoup
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from ..auth import get_current_household
from ..llm import extract_recipe
from ..models import Household

_uploads_dir = Path(__file__).resolve().parent.parent.parent.parent / "data" / "uploads"

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/recipes", tags=["recipes"])


class ImportRequest(BaseModel):
    url: str | None = None
    text: str | None = None


class ImportIngredient(BaseModel):
    name: str
    quantity: float = 1
    unit: str = "x"


class ImportResponse(BaseModel):
    name: str
    description: str = ""
    ingredients: list[ImportIngredient] = []
    image_url: str | None = None


def _extract_jsonld_recipe(html: str) -> dict | None:
    """Try to extract a schema.org Recipe from JSON-LD in the HTML."""
    soup = BeautifulSoup(html, "html.parser")
    for script in soup.find_all("script", type="application/ld+json"):
        try:
            data = json.loads(script.string)
        except (json.JSONDecodeError, TypeError):
            continue

        # Handle both direct Recipe and @graph arrays
        candidates = []
        if isinstance(data, list):
            candidates = data
        elif isinstance(data, dict):
            if data.get("@type") == "Recipe":
                return data
            candidates = data.get("@graph", [])

        for item in candidates:
            if isinstance(item, dict) and item.get("@type") == "Recipe":
                return item
    return None


_STRIP_TAGS = {"script", "style", "nav", "footer", "header", "aside", "form",
               "iframe", "noscript", "svg", "button", "input", "select",
               "textarea", "meta", "link", "figure", "img", "video", "audio",
               "picture", "source", "canvas", "map", "object", "embed"}

_CONTENT_TAGS = {"p", "li", "td", "th", "h1", "h2", "h3", "h4", "h5", "h6",
                 "dt", "dd", "blockquote", "figcaption", "pre"}


def _html_to_text(html: str) -> str:
    """Extract meaningful text content from HTML, discarding chrome/boilerplate."""
    soup = BeautifulSoup(html, "html.parser")

    # Remove non-content elements
    for tag in soup.find_all(lambda t: t.name in _STRIP_TAGS):
        tag.decompose()

    # Remove common ad/sidebar class patterns
    for tag in soup.find_all(class_=lambda c: c and any(
        kw in " ".join(c).lower() for kw in (
            "sidebar", "widget", "advert", "cookie", "popup", "modal",
            "social", "share", "comment", "related", "newsletter",
            "signup", "promo", "banner",
        )
    )):
        tag.decompose()

    # Try to find a focused content area
    main = (soup.find("main")
            or soup.find("article")
            or soup.find(attrs={"role": "main"})
            or soup.find(class_=lambda c: c and any(
                kw in " ".join(c).lower() for kw in ("recipe", "content", "entry", "post")
            )))
    root = main or soup.body or soup

    # Walk only content-bearing tags, preserving structure with line breaks
    lines = []
    for el in root.descendants:
        if el.name and el.name in _CONTENT_TAGS:
            text = el.get_text(separator=" ", strip=True)
            if text and len(text) > 1:
                prefix = ""
                if el.name.startswith("h"):
                    prefix = "#" * int(el.name[1]) + " "
                elif el.name == "li":
                    prefix = "- "
                lines.append(prefix + text)

    if lines:
        # Deduplicate consecutive identical lines
        deduped = [lines[0]]
        for line in lines[1:]:
            if line != deduped[-1]:
                deduped.append(line)
        return "\n".join(deduped)

    # Ultimate fallback: just get all text
    return root.get_text(separator="\n", strip=True)


async def _fetch_html(url: str) -> str:
    async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
        resp = await client.get(url, headers={"User-Agent": "Mozilla/5.0"})
        resp.raise_for_status()
    return resp.text


@router.post("/import", response_model=ImportResponse)
async def import_recipe(
    req: ImportRequest,
    household: Household = Depends(get_current_household),
):
    logger.info("Import request: url=%s, text=%s", req.url, bool(req.text))

    if not req.url and not req.text:
        raise HTTPException(status_code=400, detail="Provide either url or text")

    text: str
    if req.url:
        try:
            html = await _fetch_html(req.url)
        except httpx.HTTPError as e:
            logger.error("Failed to fetch URL %s: %s", req.url, e)
            raise HTTPException(status_code=400, detail=f"Failed to fetch URL: {e}")

        # Try JSON-LD first — encode as TOON for compact LLM input
        jsonld = _extract_jsonld_recipe(html)
        image_url = None
        if jsonld:
            # Extract image before cleaning for TOON
            raw_image = jsonld.get("image")
            if isinstance(raw_image, str):
                image_url = raw_image
            elif isinstance(raw_image, list) and raw_image:
                first = raw_image[0]
                if isinstance(first, str):
                    image_url = first
                elif isinstance(first, dict):
                    image_url = first.get("url")
            elif isinstance(raw_image, dict):
                image_url = raw_image.get("url")

            # Keep only recipe-relevant fields
            clean = {}
            for key in ("name", "description", "recipeIngredient",
                        "recipeInstructions", "recipeYield", "prepTime",
                        "totalTime"):
                if key in jsonld:
                    clean[key] = jsonld[key]
            text = json.dumps(clean, ensure_ascii=False)
            logger.info("Using JSON-LD (%d chars)", len(text))
        else:
            text = _html_to_text(html)
            logger.info("No JSON-LD found, using plain text (%d chars)", len(text))
    else:
        text = req.text  # type: ignore[assignment]

    # Truncate very long texts to avoid overwhelming the LLM
    if len(text) > 15000:
        text = text[:15000]

    try:
        result = await extract_recipe(text)
    except ConnectionError as e:
        logger.error("LLM worker not connected: %s", e)
        raise HTTPException(status_code=503, detail="Inference server is not connected")
    except TimeoutError as e:
        logger.error("LLM worker timeout: %s", e)
        raise HTTPException(status_code=504, detail="LLM worker did not respond in time")
    except Exception as e:
        logger.error("Recipe extraction failed: %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail=f"Recipe extraction failed: {e}")

    # Append source URL as a link at the end of the description
    if req.url:
        desc = result.get("description", "")
        link = f"[{req.url}]({req.url})"
        suffix = f"\n\n{link}" if desc else link
        result["description"] = desc + suffix

    # Download image locally if available
    if req.url and image_url:
        try:
            async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
                img_resp = await client.get(image_url, headers={"User-Agent": "Mozilla/5.0"})
                img_resp.raise_for_status()
                content_type = img_resp.headers.get("content-type", "")
                if content_type.startswith("image/"):
                    ext = "." + content_type.split("/")[1].split(";")[0].strip()
                    if ext == ".jpeg":
                        ext = ".jpg"
                    filename = f"{uuid.uuid4().hex}{ext}"
                    (_uploads_dir / filename).write_bytes(img_resp.content)
                    result["image_url"] = f"/api/uploads/{filename}"
        except Exception:
            logger.warning("Failed to download recipe image from %s", image_url)

    return result
