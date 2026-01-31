from pathlib import Path

import os

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from starlette.responses import FileResponse
from contextlib import asynccontextmanager

from .database import engine, SessionLocal
from .websocket import manager
from .auth import get_household_from_jwt
from .llm_worker_manager import llm_worker_manager
from .routers import auth, items, list, recipes, sessions, import_recipe


def _run_alembic_migrations():
    """Run Alembic migrations to head on startup."""
    import sys
    from alembic.config import Config
    from alembic import command
    from alembic.runtime.migration import MigrationContext
    from sqlalchemy import inspect

    backend_dir = str(Path(__file__).resolve().parent.parent)
    if backend_dir not in sys.path:
        sys.path.insert(0, backend_dir)

    alembic_cfg = Config(
        str(Path(__file__).resolve().parent.parent / "alembic.ini")
    )

    # If the DB already has tables but no alembic_version table,
    # stamp it at the initial migration (which matches the pre-alembic schema)
    # so that subsequent migrations still run.
    with engine.connect() as conn:
        ctx = MigrationContext.configure(conn)
        current_rev = ctx.get_current_revision()
        if current_rev is None:
            insp = inspect(engine)
            if insp.get_table_names():
                command.stamp(alembic_cfg, "91105d06de6e")

    command.upgrade(alembic_cfg, "head")


_uploads_dir = Path(__file__).resolve().parent.parent.parent / "data" / "uploads"
_uploads_dir.mkdir(parents=True, exist_ok=True)


@asynccontextmanager
async def lifespan(app: FastAPI):
    _run_alembic_migrations()
    yield


app = FastAPI(title="Nákupák API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(items.router)
app.include_router(list.router)
app.include_router(recipes.router)
app.include_router(sessions.router)
app.include_router(import_recipe.router)


@app.websocket("/api/ws")
async def websocket_endpoint(websocket: WebSocket, token: str = Query(None)):
    if not token:
        await websocket.close(code=1008)
        return

    db = SessionLocal()
    try:
        household = get_household_from_jwt(token, db)
    finally:
        db.close()

    if not household:
        await websocket.close(code=1008)
        return

    household_id = household.id
    await manager.connect(websocket, household_id)
    try:
        while True:
            data = await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket, household_id)


WORKER_SECRET = os.environ.get("WORKER_SECRET", "dev-worker-secret")


@app.websocket("/api/ws/llm-worker")
async def llm_worker_endpoint(websocket: WebSocket, token: str = Query(None)):
    if not WORKER_SECRET or token != WORKER_SECRET:
        await websocket.close(code=1008)
        return

    await websocket.accept()
    await llm_worker_manager.register(websocket)
    try:
        while True:
            raw = await websocket.receive_text()
            llm_worker_manager.handle_message(raw)
    except WebSocketDisconnect:
        await llm_worker_manager.unregister(websocket)


@app.get("/api/health")
def health_check():
    return {"status": "ok"}


# Serve uploaded files
app.mount("/api/uploads", StaticFiles(directory=_uploads_dir), name="uploads")

# Serve frontend static files (production: built frontend is at ../frontend/dist)
_frontend_dist = Path(__file__).resolve().parent.parent.parent / "frontend" / "dist"
if _frontend_dist.is_dir():
    app.mount("/assets", StaticFiles(directory=_frontend_dist / "assets"), name="assets")

    @app.get("/{full_path:path}")
    async def serve_spa(full_path: str):
        file_path = _frontend_dist / full_path
        if file_path.is_file():
            return FileResponse(file_path)
        return FileResponse(_frontend_dist / "index.html")
