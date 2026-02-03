"""LLM worker: connects to the server via WebSocket and processes Ollama prompts."""

import asyncio
import json
import logging
import os

import httpx
import websockets

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger(__name__)

SERVER_WS_URL = os.environ.get("SERVER_WS_URL", "ws://localhost:8000/api/ws/llm-worker")
WORKER_SECRET = os.environ.get("WORKER_SECRET", "dev-worker-secret")
OLLAMA_URL = os.environ.get("OLLAMA_URL", "http://localhost:11434")
LLM_MODEL = os.environ.get("LLM_MODEL", "qwen3:8b")

RECONNECT_DELAY = 5

EXTRACT_PROMPT = """\
Extract the recipe from the following text. Return ONLY a JSON object with these three keys: "name", "description", "ingredients".

- "name": recipe name
- "description": the cooking steps/instructions as plain text
- "ingredients": array of ALL ingredients, each with "name" (string), "quantity" (number), and "unit" (string)
  - Keep the original units from the recipe (g, kg, ml, l, tablespoon, cup, oz, etc.)
  - Use "x" only for countable items like "4 eggs"

The "ingredients" array is REQUIRED.

Text:
"""

FIXUP_PROMPT = """\
Reformat this recipe JSON. Return ONLY valid JSON with EXACTLY 3 keys: "name", "description", "ingredients".

Required schema:
{"name": "string", "description": "markdown string", "ingredients": [{"name": "string", "quantity": number, "unit": "string"}]}

Rules for ingredients:
- "quantity" MUST be a number (not a string). Parse "300 g mascarpone" → quantity: 300, unit: "g", name: "mascarpone"
- "unit" MUST be one of: "x", "g", "kg", "ml", "l"
- Convert units: tablespoon→15 ml, teaspoon→5 ml, cup→240 ml, oz→28 g, lb→0.45 kg
- Use base ingredient name only (e.g. "mascarpone" not "500g mascarpone cheese")

Rules for description:
- Rewrite as clean, concise markdown with numbered steps
- Do NOT include ingredients in the description
- Keep it short — just the cooking steps and key tips

Rules for name/keys:
- If the original has "title" or "recipeName" instead of "name", use that value
- Remove any extra keys (nutrition, servings, etc.)

JSON to reformat:
"""

VALID_UNITS = {"x", "g", "kg", "ml", "l"}


async def ollama_generate(prompt: str) -> str:
    """Send a prompt to local Ollama and return the response text."""
    async with httpx.AsyncClient(timeout=120.0) as client:
        response = await client.post(
            f"{OLLAMA_URL}/api/generate",
            json={
                "model": LLM_MODEL,
                "prompt": prompt,
                "stream": False,
                "format": "json",
            },
        )
        response.raise_for_status()
    return response.json().get("response", "")


def postprocess_recipe(data: dict) -> dict:
    """Validate units, coerce quantities, and clean up ingredients."""
    ingredients = []
    for ing in data.get("ingredients", []):
        if not ing.get("name"):
            continue
        try:
            qty = float(ing.get("quantity", 1))
        except (ValueError, TypeError):
            qty = 1.0
        unit = str(ing.get("unit", "x")).strip()
        if unit not in VALID_UNITS:
            unit = "x"
        ingredients.append(
            {
                "name": str(ing["name"]),
                "quantity": qty,
                "unit": unit,
            }
        )

    return {
        "name": data.get("name", "Imported Recipe"),
        "description": data.get("description", ""),
        "ingredients": ingredients,
    }


async def handle_extract_recipe(text: str) -> dict:
    """Two-pass LLM extraction: extract → validate → fixup → validate → postprocess."""
    # First pass: extract raw recipe data from source text
    raw = await ollama_generate(EXTRACT_PROMPT + text)

    try:
        json.loads(raw)
    except json.JSONDecodeError:
        logger.error("LLM returned invalid JSON: %s", raw[:500])
        raise ValueError("LLM returned invalid JSON response")

    # Second pass: reformat schema, normalize units, clean up markdown description
    logger.info("Running fixup pass on LLM output")
    raw2 = await ollama_generate(FIXUP_PROMPT + raw)
    try:
        data = json.loads(raw2)
    except json.JSONDecodeError:
        logger.warning("Fixup pass returned invalid JSON, falling back to first pass")
        data = json.loads(raw)

    return postprocess_recipe(data)


async def handle_request(msg: dict) -> dict:
    """Process a single request and return the response dict."""
    request_id = msg["request_id"]
    action = msg.get("action")

    if action == "generate":
        prompt = msg.get("prompt", "")
        logger.info(
            "Processing generate request %s (%d chars)", request_id, len(prompt)
        )
        try:
            result = await ollama_generate(prompt)
            logger.info(
                "Completed request %s (%d chars response)", request_id, len(result)
            )
            return {"request_id": request_id, "result": result}
        except Exception as e:
            logger.error("Ollama error for request %s: %s", request_id, e)
            return {"request_id": request_id, "error": str(e)}

    if action == "extract_recipe":
        text = msg.get("text", "")
        logger.info(
            "Processing extract_recipe request %s (%d chars)", request_id, len(text)
        )
        try:
            result = await handle_extract_recipe(text)
            logger.info("Completed extract_recipe request %s", request_id)
            return {"request_id": request_id, "result": result}
        except Exception as e:
            logger.error("extract_recipe error for request %s: %s", request_id, e)
            return {"request_id": request_id, "error": str(e)}

    return {"request_id": request_id, "error": f"Unknown action: {action}"}


async def worker_loop():
    """Connect to server and process requests. Reconnects on failure."""
    url = f"{SERVER_WS_URL}?token={WORKER_SECRET}"

    while True:
        try:
            logger.info("Connecting to %s", SERVER_WS_URL)
            async with websockets.connect(url) as ws:
                logger.info("Connected to server")
                async for raw in ws:
                    try:
                        msg = json.loads(raw)
                    except json.JSONDecodeError:
                        logger.warning("Invalid JSON from server: %s", raw[:200])
                        continue

                    response = await handle_request(msg)
                    await ws.send(json.dumps(response))

        except (websockets.ConnectionClosed, ConnectionError, OSError) as e:
            logger.warning("Disconnected: %s", e)
        except Exception as e:
            logger.error("Unexpected error: %s", e)

        logger.info("Reconnecting in %ds...", RECONNECT_DELAY)
        await asyncio.sleep(RECONNECT_DELAY)


def main():
    asyncio.run(worker_loop())


if __name__ == "__main__":
    main()
