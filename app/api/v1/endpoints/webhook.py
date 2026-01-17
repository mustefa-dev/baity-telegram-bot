from fastapi import APIRouter, BackgroundTasks

from app.api.deps import ApiKeyDep, TelegramServiceDep
from app.core.logging import get_logger
from app.schemas.realestate import RealestateWebhook
from app.schemas.response import WebhookResponse, WebhookStatus

router = APIRouter()
logger = get_logger(__name__)


@router.post(
    "/realestate",
    response_model=WebhookResponse,
    summary="Post real estate to Telegram",
    description="Receive a real estate listing and post it to the appropriate Telegram channel.",
    responses={
        200: {"description": "Successfully processed webhook"},
        401: {"description": "Invalid or missing API key"},
        422: {"description": "Validation error"},
        429: {"description": "Rate limited by Telegram"},
        502: {"description": "Telegram API error"},
    },
)
async def handle_realestate_webhook(
    payload: RealestateWebhook,
    _api_key: ApiKeyDep,
    telegram_service: TelegramServiceDep,
) -> WebhookResponse:
    """
    Handle incoming real estate webhook.

    This endpoint receives real estate data and posts it to the
    corresponding city's Telegram channel.

    **Authentication**: Requires `X-Api-Key` header.

    **City Channel Mapping**: The city_id is used to determine
    which Telegram channel to post to. If no channel is configured
    for the city, the webhook will be skipped.
    """
    logger.info(f"Received webhook for realestate {payload.id} in city {payload.city_id}")

    result = await telegram_service.post_realestate(payload)

    return result


@router.post(
    "/realestate/async",
    response_model=WebhookResponse,
    summary="Post real estate to Telegram (async)",
    description="Queue a real estate listing to be posted to Telegram asynchronously.",
)
async def handle_realestate_webhook_async(
    payload: RealestateWebhook,
    _api_key: ApiKeyDep,
    telegram_service: TelegramServiceDep,
    background_tasks: BackgroundTasks,
) -> WebhookResponse:
    """
    Handle incoming real estate webhook asynchronously.

    This endpoint queues the real estate posting as a background task,
    allowing for faster response times. Use this for non-critical
    notifications where immediate confirmation isn't required.

    **Authentication**: Requires `X-Api-Key` header.
    """
    logger.info(f"Queuing async webhook for realestate {payload.id}")

    async def post_task() -> None:
        try:
            await telegram_service.post_realestate(payload)
        except Exception as e:
            logger.error(f"Background task failed for {payload.id}: {e}")

    background_tasks.add_task(post_task)

    return WebhookResponse(
        status=WebhookStatus.QUEUED,
        message="Webhook queued for processing",
    )


@router.post(
    "/realestate/batch",
    response_model=list[WebhookResponse],
    summary="Post multiple real estates to Telegram",
    description="Receive multiple real estate listings and post them to Telegram.",
)
async def handle_realestate_batch_webhook(
    payloads: list[RealestateWebhook],
    _api_key: ApiKeyDep,
    telegram_service: TelegramServiceDep,
) -> list[WebhookResponse]:
    """
    Handle batch real estate webhook.

    This endpoint receives multiple real estate listings and posts them
    to their corresponding Telegram channels. Each listing is processed
    independently, so failures in one won't affect others.

    **Authentication**: Requires `X-Api-Key` header.

    **Rate Limiting**: Be mindful of Telegram's rate limits when using
    batch endpoints. Consider using the async endpoint for large batches.
    """
    logger.info(f"Received batch webhook with {len(payloads)} items")

    results = []
    for payload in payloads:
        result = await telegram_service.post_realestate(payload)
        results.append(result)

    return results
