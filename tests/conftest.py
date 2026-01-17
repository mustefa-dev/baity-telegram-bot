import os
from typing import AsyncGenerator, Generator
from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi.testclient import TestClient
from httpx import AsyncClient

# Set test environment before importing app
os.environ["ENVIRONMENT"] = "development"
os.environ["DEBUG"] = "true"
os.environ["BOT_TOKEN"] = "1234567890:ABCdefGHIjklMNOpqrsTUVwxyz1234567890"
os.environ["WEBHOOK_API_KEY"] = "test-api-key-12345678"

from app.main import app
from app.api.deps import get_telegram_service
from app.services.telegram import TelegramService


@pytest.fixture
def mock_telegram_service() -> MagicMock:
    """Create a mock Telegram service."""
    service = MagicMock(spec=TelegramService)
    service.health_check = AsyncMock(return_value=True)
    service.post_realestate = AsyncMock(return_value=MagicMock(
        status="posted",
        message="Successfully posted to Telegram",
        message_id=12345,
        channel_id="@test_channel",
    ))
    return service


@pytest.fixture
def client(mock_telegram_service: MagicMock) -> Generator[TestClient, None, None]:
    """Create a test client with mocked dependencies."""
    app.dependency_overrides[get_telegram_service] = lambda: mock_telegram_service
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
async def async_client(mock_telegram_service: MagicMock) -> AsyncGenerator[AsyncClient, None]:
    """Create an async test client with mocked dependencies."""
    app.dependency_overrides[get_telegram_service] = lambda: mock_telegram_service
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()


@pytest.fixture
def valid_api_key() -> str:
    """Return the valid test API key."""
    return "test-api-key-12345678"


@pytest.fixture
def sample_realestate_payload() -> dict:
    """Return a sample real estate webhook payload."""
    return {
        "id": "abc123xyz",
        "title": "Modern Apartment in Baghdad",
        "description": "Spacious 3-bedroom apartment with city view",
        "price": 150000000,
        "currency": "IQD",
        "area": 180.5,
        "city_id": 1,
        "city_name": "Baghdad",
        "district_name": "Al-Mansour",
        "subdistrict_name": "Al-Jamia",
        "category": "Residential",
        "subcategory": "Apartment",
        "images": ["https://example.com/image1.jpg"],
        "offer_type": "SELL",
        "phone": "+964123456789",
        "url": "https://ibaity.com/realestate/abc123xyz"
    }
