import asyncio
import pytest
from unittest.mock import AsyncMock
from app.websocket import ConnectionManager


def test_websocket_connect_valid_token(client, household, auth_headers):
    token = auth_headers["Authorization"].replace("Bearer ", "")
    with client.websocket_connect(f"/api/ws?token={token}") as ws:
        assert ws is not None


def test_websocket_missing_token(client):
    with pytest.raises(Exception):
        with client.websocket_connect("/api/ws") as ws:
            ws.receive_text()


def test_websocket_invalid_token(client):
    with pytest.raises(Exception):
        with client.websocket_connect("/api/ws?token=invalid.jwt.here") as ws:
            ws.receive_text()


def test_connection_manager_connect():
    mgr = ConnectionManager()
    ws = AsyncMock()
    asyncio.get_event_loop().run_until_complete(mgr.connect(ws, 1))
    assert 1 in mgr.active_connections
    assert ws in mgr.active_connections[1]


def test_connection_manager_disconnect():
    mgr = ConnectionManager()
    ws = AsyncMock()
    asyncio.get_event_loop().run_until_complete(mgr.connect(ws, 1))
    mgr.disconnect(ws, 1)
    assert 1 not in mgr.active_connections


def test_connection_manager_broadcast():
    mgr = ConnectionManager()
    ws1 = AsyncMock()
    ws2 = AsyncMock()
    loop = asyncio.get_event_loop()
    loop.run_until_complete(mgr.connect(ws1, 1))
    loop.run_until_complete(mgr.connect(ws2, 1))
    loop.run_until_complete(mgr.broadcast(1, {"type": "test"}))
    ws1.send_json.assert_called_once_with({"type": "test"})
    ws2.send_json.assert_called_once_with({"type": "test"})


def test_connection_manager_household_isolation():
    mgr = ConnectionManager()
    ws1 = AsyncMock()
    ws2 = AsyncMock()
    loop = asyncio.get_event_loop()
    loop.run_until_complete(mgr.connect(ws1, 1))
    loop.run_until_complete(mgr.connect(ws2, 2))
    loop.run_until_complete(mgr.broadcast(1, {"type": "test"}))
    ws1.send_json.assert_called_once()
    ws2.send_json.assert_not_called()
