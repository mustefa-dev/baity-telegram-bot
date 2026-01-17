from fastapi import APIRouter

from app.api.deps import SettingsDep, TelegramServiceDep
from app.schemas.response import HealthResponse

router = APIRouter()


@router.get(
    "",
    response_model=HealthResponse,
    summary="Health check",
    description="Check the health status of the application and its dependencies.",
)
async def health_check(
    settings: SettingsDep,
    telegram_service: TelegramServiceDep,
) -> HealthResponse:
    """
    Perform health check on the application.

    Returns the application status and checks for:
    - Telegram bot connectivity
    - Configuration validity
    """
    checks = {
        "configuration": True,
    }

    # Check Telegram bot
    try:
        checks["telegram_bot"] = await telegram_service.health_check()
    except Exception:
        checks["telegram_bot"] = False

    # Determine overall status
    all_healthy = all(checks.values())

    return HealthResponse(
        status="ok" if all_healthy else "degraded",
        version=settings.APP_VERSION,
        environment=settings.ENVIRONMENT,
        checks=checks,
    )


@router.get(
    "/ready",
    summary="Readiness check",
    description="Check if the application is ready to receive traffic.",
)
async def readiness_check() -> dict[str, str]:
    """Simple readiness check for load balancers."""
    return {"status": "ready"}


@router.get(
    "/live",
    summary="Liveness check",
    description="Check if the application is alive.",
)
async def liveness_check() -> dict[str, str]:
    """Simple liveness check for container orchestration."""
    return {"status": "alive"}
