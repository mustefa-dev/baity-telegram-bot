import asyncio
from typing import Any

from telegram import Bot
from telegram.constants import ParseMode
from telegram.error import RetryAfter, TelegramError as TelegramAPIError

from app.core.config import settings
from app.core.exceptions import (
    ChannelNotFoundError,
    TelegramError,
    TelegramRateLimitError,
)
from app.core.logging import get_logger
from app.schemas.realestate import RealestateWebhook
from app.schemas.response import WebhookResponse, WebhookStatus
from app.services.base import MessageService
from app.services.message_formatter import ArabicMessageFormatter, MessageFormatter

logger = get_logger(__name__)


class TelegramService(MessageService):
    """Service for interacting with Telegram Bot API."""

    def __init__(
        self,
        bot_token: str | None = None,
        formatter: MessageFormatter | None = None,
        max_retries: int | None = None,
        retry_delay: float | None = None,
    ) -> None:
        super().__init__()
        self._bot_token = bot_token or settings.BOT_TOKEN
        self._bot: Bot | None = None
        self._formatter = formatter or ArabicMessageFormatter()
        self._max_retries = max_retries or settings.MAX_RETRIES
        self._retry_delay = retry_delay or settings.RETRY_DELAY

    @property
    def bot(self) -> Bot:
        """Lazy initialization of the bot instance."""
        if self._bot is None:
            self._bot = Bot(token=self._bot_token)
        return self._bot

    async def health_check(self) -> bool:
        """Check if the Telegram bot is accessible."""
        try:
            me = await self.bot.get_me()
            logger.debug(f"Bot health check passed: @{me.username}")
            return True
        except Exception as e:
            logger.error(f"Bot health check failed: {e}")
            return False

    async def send_message(
        self,
        channel_id: str,
        message: str,
        parse_mode: str = ParseMode.HTML,
        disable_web_page_preview: bool = False,
        **kwargs: Any,
    ) -> int | None:
        """Send a text message to a Telegram channel."""
        return await self._send_with_retry(
            self.bot.send_message,
            chat_id=channel_id,
            text=message,
            parse_mode=parse_mode,
            disable_web_page_preview=disable_web_page_preview,
            **kwargs,
        )

    async def send_photo(
        self,
        channel_id: str,
        photo_url: str,
        caption: str | None = None,
        parse_mode: str = ParseMode.HTML,
        **kwargs: Any,
    ) -> int | None:
        """Send a photo with optional caption to a Telegram channel."""
        return await self._send_with_retry(
            self.bot.send_photo,
            chat_id=channel_id,
            photo=photo_url,
            caption=caption,
            parse_mode=parse_mode,
            **kwargs,
        )

    async def send_media_group(
        self,
        channel_id: str,
        media: list[Any],
        **kwargs: Any,
    ) -> list[int]:
        """Send a group of photos/videos to a Telegram channel."""
        try:
            messages = await self.bot.send_media_group(
                chat_id=channel_id,
                media=media,
                **kwargs,
            )
            return [msg.message_id for msg in messages]
        except Exception as e:
            logger.error(f"Failed to send media group: {e}")
            raise TelegramError(f"Failed to send media group: {e}")

    async def post_realestate(
        self,
        data: RealestateWebhook,
        channel_id: str | None = None,
    ) -> WebhookResponse:
        """Post a real estate listing to Telegram."""
        # Get channel for city if not provided
        if channel_id is None:
            channel_id = settings.get_channel_for_city(data.city_id)

        if not channel_id:
            logger.warning(f"No channel configured for city ID {data.city_id}")
            return WebhookResponse(
                status=WebhookStatus.SKIPPED,
                message=f"No channel configured for city ID {data.city_id}",
            )

        try:
            message = self._formatter.format(data)
            message_id: int | None = None

            if data.images:
                # Send with first image
                message_id = await self.send_photo(
                    channel_id=channel_id,
                    photo_url=data.images[0],
                    caption=message,
                )
            else:
                # Send text only
                message_id = await self.send_message(
                    channel_id=channel_id,
                    message=message,
                )

            if message_id:
                logger.info(
                    f"Posted realestate {data.id} to {channel_id}, message_id={message_id}"
                )
                return WebhookResponse(
                    status=WebhookStatus.POSTED,
                    message="Successfully posted to Telegram",
                    message_id=message_id,
                    channel_id=channel_id,
                )
            else:
                return WebhookResponse(
                    status=WebhookStatus.FAILED,
                    message="Failed to post to Telegram",
                    channel_id=channel_id,
                )

        except TelegramRateLimitError as e:
            logger.warning(f"Rate limited, retry after {e.retry_after}s")
            return WebhookResponse(
                status=WebhookStatus.FAILED,
                message=f"Rate limited, retry after {e.retry_after} seconds",
                channel_id=channel_id,
            )
        except TelegramError as e:
            logger.error(f"Telegram error: {e}")
            return WebhookResponse(
                status=WebhookStatus.FAILED,
                message=str(e),
                channel_id=channel_id,
            )
        except Exception as e:
            logger.exception(f"Unexpected error posting to Telegram: {e}")
            return WebhookResponse(
                status=WebhookStatus.FAILED,
                message=f"Unexpected error: {str(e)}",
                channel_id=channel_id,
            )

    async def _send_with_retry(
        self,
        method: Any,
        **kwargs: Any,
    ) -> int | None:
        """Execute a send method with retry logic."""
        last_exception: Exception | None = None

        for attempt in range(self._max_retries):
            try:
                result = await method(**kwargs)
                return result.message_id if hasattr(result, "message_id") else None

            except RetryAfter as e:
                logger.warning(
                    f"Rate limited, waiting {e.retry_after}s (attempt {attempt + 1}/{self._max_retries})"
                )
                if attempt < self._max_retries - 1:
                    await asyncio.sleep(e.retry_after)
                else:
                    raise TelegramRateLimitError(e.retry_after)

            except TelegramAPIError as e:
                last_exception = e
                logger.error(
                    f"Telegram API error (attempt {attempt + 1}/{self._max_retries}): {e}"
                )
                if attempt < self._max_retries - 1:
                    await asyncio.sleep(self._retry_delay * (attempt + 1))
                else:
                    raise TelegramError(f"Telegram API error: {e}")

            except Exception as e:
                last_exception = e
                logger.error(
                    f"Unexpected error (attempt {attempt + 1}/{self._max_retries}): {e}"
                )
                if attempt < self._max_retries - 1:
                    await asyncio.sleep(self._retry_delay * (attempt + 1))

        raise TelegramError(
            f"Failed after {self._max_retries} attempts: {last_exception}"
        )
