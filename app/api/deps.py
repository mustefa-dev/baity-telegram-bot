from functools import lru_cache
from typing import Annotated

from fastapi import Depends, Header, HTTPException, status

from app.core.config import Settings, get_settings
from app.core.exceptions import AuthenticationError
from app.services.message_formatter import MessageFormatter
from app.services.telegram import TelegramService


def get_api_key(
    x_api_key: Annotated[str | None, Header()] = None,
    settings: Settings = Depends(get_settings),
) -> str:
    """Validate and return the API key."""
    if not x_api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing API key",
            headers={"WWW-Authenticate": "ApiKey"},
        )

    if x_api_key != settings.WEBHOOK_API_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key",
            headers={"WWW-Authenticate": "ApiKey"},
        )

    return x_api_key


@lru_cache
def get_message_formatter() -> MessageFormatter:
    """Get cached message formatter instance."""
    return MessageFormatter()


@lru_cache
def get_telegram_service() -> TelegramService:
    """Get cached Telegram service instance."""
    settings = get_settings()
    formatter = get_message_formatter()
    return TelegramService(
        bot_token=settings.BOT_TOKEN,
        formatter=formatter,
    )


# Type aliases for dependency injection
SettingsDep = Annotated[Settings, Depends(get_settings)]
ApiKeyDep = Annotated[str, Depends(get_api_key)]
TelegramServiceDep = Annotated[TelegramService, Depends(get_telegram_service)]
MessageFormatterDep = Annotated[MessageFormatter, Depends(get_message_formatter)]
