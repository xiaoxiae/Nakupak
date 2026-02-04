from .llm_worker_manager import llm_worker_manager


async def extract_recipe(text: str, language: str | None = None) -> dict:
    """Extract recipe data from text using the remote LLM worker."""
    payload = {"text": text}
    if language:
        payload["language"] = language
    return await llm_worker_manager.send_request("extract_recipe", payload)
