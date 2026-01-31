from .llm_worker_manager import llm_worker_manager


async def extract_recipe(text: str) -> dict:
    """Extract recipe data from text using the remote LLM worker."""
    return await llm_worker_manager.send_request("extract_recipe", {"text": text})
