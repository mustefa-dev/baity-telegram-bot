from abc import ABC, abstractmethod
from typing import Any, Generic, TypeVar

from app.core.logging import get_logger

T = TypeVar("T")
R = TypeVar("R")


class BaseService(ABC):
    """Base class for all services."""

    def __init__(self) -> None:
        self.logger = get_logger(self.__class__.__name__)

    @abstractmethod
    async def health_check(self) -> bool:
        """Check if the service is healthy."""
        pass


class MessageService(BaseService, ABC):
    """Base class for messaging services."""

    @abstractmethod
    async def send_message(
        self,
        channel_id: str,
        message: str,
        **kwargs: Any
    ) -> int | None:
        """Send a message to a channel. Returns message ID if successful."""
        pass

    @abstractmethod
    async def send_photo(
        self,
        channel_id: str,
        photo_url: str,
        caption: str | None = None,
        **kwargs: Any
    ) -> int | None:
        """Send a photo to a channel. Returns message ID if successful."""
        pass
