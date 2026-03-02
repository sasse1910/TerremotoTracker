from fastapi import APIRouter

from app.api.v1.endpoints import earthquakes, health, volcanoes, ws

router = APIRouter()

router.include_router(earthquakes.router, prefix="/earthquakes", tags=["Earthquakes"])
router.include_router(volcanoes.router, prefix="/volcanoes", tags=["Volcanoes"])
router.include_router(health.router, tags=["Health"])
router.include_router(ws.router, tags=["WebSocket"])
