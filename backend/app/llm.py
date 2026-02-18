import json
import logging
import os

from anthropic import AsyncAnthropic

logger = logging.getLogger(__name__)

ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY")
MODEL = "claude-haiku-4-5-20251001"

VALID_UNITS = {"x", "g", "kg", "ml", "l"}

EXTRACT_SYSTEM_PROMPT = """\
You are a recipe extraction assistant. Given raw text (which may be JSON-LD, HTML content, or plain text), extract the recipe and return a JSON object with exactly these keys:

- "name": the recipe name (string)
- "ingredients": array of ingredients, each with:
  - "name": base ingredient name only (e.g. "mascarpone" not "500g mascarpone cheese")
  - "quantity": a number (parse "300 g mascarpone" → 300)
  - "unit": one of "x", "g", "kg", "ml", "l"
    - Convert: tablespoon→15 ml, teaspoon→5 ml, cup→240 ml, oz→28 g, lb→454 g
    - Use "x" for countable items (e.g. "4 eggs" → quantity: 4, unit: "x")
- "description": markdown-formatted cooking instructions
  - Include ALL steps with full detail: temperatures, times, techniques, tips
  - Do NOT include recipe name or ingredients list in the description
  - Use proper markdown formatting (numbered lists, bold, etc.)

Return ONLY valid JSON, nothing else."""

TRANSLATE_SYSTEM_PROMPT = """\
Translate the following JSON into {language}. Return ONLY a JSON object with the exact same structure.

The JSON has three keys:
- "name": a string — translate it
- "ingredients": an array of strings — translate each one
- "description": a string — translate it

Return ONLY the translated JSON, nothing else."""


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
        "description": data.get("description", "").strip(),
        "ingredients": ingredients,
    }


async def extract_recipe(text: str, language: str | None = None) -> dict:
    """Extract recipe data from text using the Anthropic API."""
    if not ANTHROPIC_API_KEY:
        raise ConnectionError("Anthropic API key is not configured")

    client = AsyncAnthropic(api_key=ANTHROPIC_API_KEY)

    # Single extraction call
    logger.info("Extracting recipe via Anthropic API (%d chars input)", len(text))
    response = await client.messages.create(
        model=MODEL,
        max_tokens=4096,
        system=EXTRACT_SYSTEM_PROMPT,
        messages=[{"role": "user", "content": text}],
    )

    raw = response.content[0].text
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        logger.error("LLM returned invalid JSON: %s", raw[:500])
        raise ValueError("LLM returned invalid JSON response")

    result = postprocess_recipe(data)

    # Optional translation pass
    if language:
        logger.info("Running translation pass to %s", language)
        to_translate = {
            "name": result["name"],
            "ingredients": [ing["name"] for ing in result["ingredients"]],
            "description": result["description"],
        }
        translate_response = await client.messages.create(
            model=MODEL,
            max_tokens=4096,
            system=TRANSLATE_SYSTEM_PROMPT.format(language=language),
            messages=[
                {
                    "role": "user",
                    "content": json.dumps(to_translate, ensure_ascii=False),
                }
            ],
        )
        try:
            translated = json.loads(translate_response.content[0].text)
            result["name"] = translated.get("name", result["name"])
            result["description"] = translated.get("description", result["description"])
            translated_names = translated.get("ingredients", [])
            for i, name in enumerate(translated_names):
                if i < len(result["ingredients"]) and isinstance(name, str):
                    result["ingredients"][i]["name"] = name
        except (json.JSONDecodeError, KeyError, TypeError):
            logger.warning("Translation pass failed, keeping original language")

    return result
