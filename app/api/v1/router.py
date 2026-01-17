from fastapi import APIRouter

from app.api.v1.endpoints import health, webhook

api_router = APIRouter()

# Include endpoint routers
api_router.include_router(
    health.router,
    prefix="/health",
    tags=["Health"],
)

api_router.include_router(
    webhook.router,
    prefix="/webhook",
    tags=["Webhook"],
)
