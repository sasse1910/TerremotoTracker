import pytest
from starlette.testclient import TestClient

from app.main import app


@pytest.mark.unit
def test_websocket_connect_and_ping_pong() -> None:
    with TestClient(app) as test_client:
        with test_client.websocket_connect("/api/v1/ws/live") as ws:
            ws.send_text("ping")
            assert ws.receive_text() == "pong"


@pytest.mark.unit
def test_websocket_multiple_messages() -> None:
    with TestClient(app) as test_client:
        with test_client.websocket_connect("/api/v1/ws/live") as ws:
            for _ in range(3):
                ws.send_text("ping")
                assert ws.receive_text() == "pong"


@pytest.mark.unit
def test_websocket_disconnect_is_clean() -> None:
    with TestClient(app) as test_client:
        with test_client.websocket_connect("/api/v1/ws/live"):
            pass
