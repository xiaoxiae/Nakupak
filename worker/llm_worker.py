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
/no_think
Extract the recipe from the following text. Return ONLY a JSON object with these two keys: "name", "ingredients".

- "name": recipe name
- "ingredients": array of ALL ingredients, each with "name" (string), "quantity" (number), and "unit" (string)
  - "quantity" MUST be a number (not a string). Parse "300 g mascarpone" → quantity: 300, unit: "g", name: "mascarpone"
  - Keep the original units from the recipe (g, kg, ml, l, tablespoon, cup, oz, etc.)
  - Use "x" only for countable items like "4 eggs"
  - Use base ingredient name only (e.g. "mascarpone" not "500g mascarpone cheese")

The "ingredients" array is REQUIRED.

Text:
"""

FIXUP_DATA_PROMPT = """\
/no_think
Reformat this recipe JSON. Return ONLY valid JSON with EXACTLY 2 keys: "name", "ingredients".

Required schema:
{"name": "string", "ingredients": [{"name": "string", "quantity": number, "unit": "string"}]}

Rules for ingredients:
- "quantity" MUST be a number (not a string). Parse "300 g mascarpone" → quantity: 300, unit: "g", name: "mascarpone"
- "unit" MUST be one of: "x", "g", "kg", "ml", "l"
- Convert units: tablespoon→15 ml, teaspoon→5 ml, cup→240 ml, oz→28 g, lb→0.45 kg
- Use base ingredient name only (e.g. "mascarpone" not "500g mascarpone cheese")

Rules for name:
- If the original has "title" or "recipeName" instead of "name", use that value
- Remove any extra keys (nutrition, servings, description, etc.)

JSON to reformat:
"""

FIXUP_DESCRIPTION_PROMPT = """\
/no_think
Rewrite the following recipe text as a properly formatted markdown description of the cooking instructions.

Rules:
- Do NOT include the recipe name or ingredients — only the cooking steps/instructions
- Include all details: temperatures, times, techniques, and tips from the original recipe
- Do NOT summarize or shorten the instructions — preserve the full detail
- Use proper markdown formatting (numbered lists, bold, etc.)
- Output ONLY the markdown description, nothing else

Recipe text:
"""

TRANSLATE_PROMPT = """\
/no_think
Translate the following JSON into {language}. Return ONLY a JSON object with EXACTLY the same structure.

The JSON has three keys:
- "name": a string — translate it
- "ingredients": an array of strings — translate each one, keep the array length the same
- "description": a string — translate it

Return ONLY the translated JSON, nothing else.

JSON to translate:
"""

VALID_UNITS = {"x", "g", "kg", "ml", "l"}


async def ollama_generate(prompt: str, format: str | None = None) -> str:
    """Send a prompt to local Ollama and return the response text."""
    payload = {
        "model": LLM_MODEL,
        "prompt": prompt,
        "stream": False,
    }
    if format:
        payload["format"] = format
    async with httpx.AsyncClient(timeout=120.0) as client:
        response = await client.post(
            f"{OLLAMA_URL}/api/generate",
            json=payload,
        )
        response.raise_for_status()
    return response.json().get("response", "")


def postprocess_recipe(data: dict, description: str) -> dict:
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
        "description": description.strip(),
        "ingredients": ingredients,
    }


async def handle_extract_recipe(text: str, language: str | None = None) -> dict:
    """Three-pass LLM extraction (+ optional translation): extract → fixup units → description → translate."""
    # Pass 1: extract raw recipe data from source text
    raw = await ollama_generate(EXTRACT_PROMPT + text, format="json")

    try:
        json.loads(raw)
    except json.JSONDecodeError:
        logger.error("LLM returned invalid JSON: %s", raw[:500])
        raise ValueError("LLM returned invalid JSON response")

    # Pass 2: reformat name + ingredients with unit conversion (JSON mode)
    logger.info("Running data fixup pass on LLM output")
    raw2 = await ollama_generate(FIXUP_DATA_PROMPT + raw, format="json")
    try:
        data = json.loads(raw2)
    except json.JSONDecodeError:
        logger.warning("Data fixup pass returned invalid JSON, falling back to first pass")
        data = json.loads(raw)

    # Pass 3: generate markdown description (freeform mode)
    logger.info("Running description pass on original text")
    description = await ollama_generate(FIXUP_DESCRIPTION_PROMPT + text)

    result = postprocess_recipe(data, description)

    # Pass 3 (optional): translate into requested language
    if language:
        logger.info("Running translation pass to %s", language)
        # Only send translatable text — no quantities/units
        to_translate = {
            "name": result["name"],
            "ingredients": [ing["name"] for ing in result["ingredients"]],
            "description": result["description"],
        }
        prompt = TRANSLATE_PROMPT.format(language=language) + json.dumps(to_translate, ensure_ascii=False)
        translated_raw = await ollama_generate(prompt, format="json")
        try:
            translated = json.loads(translated_raw)
            result["name"] = translated.get("name", result["name"])
            result["description"] = translated.get("description", result["description"])
            translated_names = translated.get("ingredients", [])
            for i, name in enumerate(translated_names):
                if i < len(result["ingredients"]) and isinstance(name, str):
                    result["ingredients"][i]["name"] = name
        except (json.JSONDecodeError, KeyError, TypeError):
            logger.warning("Translation pass failed, keeping original language")

    return result


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
            result = await ollama_generate(prompt, format="json")
            logger.info(
                "Completed request %s (%d chars response)", request_id, len(result)
            )
            return {"request_id": request_id, "result": result}
        except Exception as e:
            logger.error("Ollama error for request %s: %s", request_id, e)
            return {"request_id": request_id, "error": str(e)}

    if action == "extract_recipe":
        text = msg.get("text", "")
        language = msg.get("language")
        logger.info(
            "Processing extract_recipe request %s (%d chars)", request_id, len(text)
        )
        try:
            result = await handle_extract_recipe(text, language=language)
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
