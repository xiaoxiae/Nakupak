import asyncio
import json
import logging
import uuid

from fastapi import WebSocket

logger = logging.getLogger(__name__)


class LLMWorkerManager:
    def __init__(self):
        self._worker: WebSocket | None = None
        self._pending: dict[str, asyncio.Future] = {}

    @property
    def connected(self) -> bool:
        return self._worker is not None

    async def register(self, ws: WebSocket):
        if self._worker is not None:
            logger.warning("Replacing existing LLM worker connection")
            await self._cancel_pending("Worker replaced by new connection")
        self._worker = ws
        logger.info("LLM worker connected")

    async def unregister(self, ws: WebSocket):
        if self._worker is ws:
            self._worker = None
            await self._cancel_pending("Worker disconnected")
            logger.info("LLM worker disconnected")

    async def _cancel_pending(self, reason: str):
        for fut in self._pending.values():
            if not fut.done():
                fut.set_exception(ConnectionError(reason))
        self._pending.clear()

    def handle_message(self, raw: str):
        try:
            msg = json.loads(raw)
        except json.JSONDecodeError:
            logger.warning("Invalid JSON from worker: %s", raw[:200])
            return

        request_id = msg.get("request_id")
        if not request_id or request_id not in self._pending:
            logger.warning("Unknown request_id from worker: %s", request_id)
            return

        fut = self._pending.pop(request_id)
        if fut.done():
            return

        if "error" in msg:
            fut.set_exception(RuntimeError(msg["error"]))
        else:
            fut.set_result(msg.get("result", ""))

    async def send_request(self, action: str, payload: dict):
        if self._worker is None:
            raise ConnectionError("Inference server is not connected")

        request_id = uuid.uuid4().hex
        fut: asyncio.Future = asyncio.get_event_loop().create_future()
        self._pending[request_id] = fut

        message = json.dumps({"request_id": request_id, "action": action, **payload})
        try:
            await self._worker.send_text(message)
        except Exception:
            self._pending.pop(request_id, None)
            if not fut.done():
                fut.cancel()
            raise ConnectionError("Failed to send request to worker")

        try:
            return await asyncio.wait_for(fut, timeout=180.0)
        except asyncio.TimeoutError:
            self._pending.pop(request_id, None)
            raise TimeoutError("LLM worker did not respond in time")


llm_worker_manager = LLMWorkerManager()
