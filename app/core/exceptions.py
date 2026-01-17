from typing import Any


class BaityBotException(Exception):
    """Base exception for the application."""

    def __init__(self, message: str, details: dict[str, Any] | None = None) -> None:
        self.message = message
        self.details = details or {}
        super().__init__(self.message)


class ConfigurationError(BaityBotException):
    """Raised when there's a configuration error."""
    pass


class TelegramError(BaityBotException):
    """Raised when there's an error communicating with Telegram."""
    pass


class TelegramRateLimitError(TelegramError):
    """Raised when Telegram rate limit is hit."""

    def __init__(self, retry_after: int) -> None:
        self.retry_after = retry_after
        super().__init__(
            f"Rate limited by Telegram. Retry after {retry_after} seconds",
            {"retry_after": retry_after}
        )


class ChannelNotFoundError(BaityBotException):
    """Raised when no channel is configured for a city."""

    def __init__(self, city_id: int) -> None:
        self.city_id = city_id
        super().__init__(
            f"No Telegram channel configured for city ID {city_id}",
            {"city_id": city_id}
        )


class AuthenticationError(BaityBotException):
    """Raised when authentication fails."""
    pass


class ValidationError(BaityBotException):
    """Raised when validation fails."""
    pass
