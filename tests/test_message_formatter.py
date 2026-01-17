import pytest

from app.schemas.realestate import RealestateWebhook
from app.services.message_formatter import MessageFormatter, ArabicMessageFormatter


class TestMessageFormatter:
    """Test message formatting."""

    @pytest.fixture
    def formatter(self) -> MessageFormatter:
        """Create a message formatter instance."""
        return MessageFormatter()

    @pytest.fixture
    def sample_data(self) -> RealestateWebhook:
        """Create sample real estate data."""
        return RealestateWebhook(
            id="abc123",
            title="Modern Apartment",
            description="A beautiful apartment with great views",
            price=150000000,
            currency="IQD",
            area=180.5,
            city_id=1,
            city_name="Baghdad",
            district_name="Al-Mansour",
            subdistrict_name="Al-Jamia",
            category="Residential",
            subcategory="Apartment",
            images=["https://example.com/image.jpg"],
            offer_type="SELL",
            phone="+964123456789",
            url="https://ibaity.com/realestate/abc123"
        )

    def test_format_basic(
        self,
        formatter: MessageFormatter,
        sample_data: RealestateWebhook,
    ) -> None:
        """Test basic message formatting."""
        message = formatter.format(sample_data)

        assert "Modern Apartment" in message
        assert "Baghdad" in message
        assert "180" in message
        assert "150,000,000" in message
        assert "IQD" in message
        assert "View Details" in message

    def test_format_escapes_html(
        self,
        formatter: MessageFormatter,
    ) -> None:
        """Test HTML escaping in titles."""
        data = RealestateWebhook(
            id="test",
            title="<script>alert('xss')</script>",
            price=100000,
            currency="IQD",
            area=100,
            city_id=1,
            city_name="Test",
            district_name="Test",
            subdistrict_name="Test",
            category="Test",
            subcategory="Test",
            images=[],
            offer_type="SELL",
            url="https://example.com"
        )

        message = formatter.format(data)

        assert "<script>" not in message
        assert "&lt;script&gt;" in message

    def test_format_truncates_description(
        self,
        formatter: MessageFormatter,
    ) -> None:
        """Test description truncation."""
        long_description = "A" * 300
        data = RealestateWebhook(
            id="test",
            title="Test",
            description=long_description,
            price=100000,
            currency="IQD",
            area=100,
            city_id=1,
            city_name="Test",
            district_name="Test",
            subdistrict_name="Test",
            category="Test",
            subcategory="Test",
            images=[],
            offer_type="SELL",
            url="https://example.com"
        )

        message = formatter.format(data)

        # Should be truncated
        assert len([c for c in message if c == "A"]) < 300
        assert "..." in message

    def test_format_zero_price(
        self,
        formatter: MessageFormatter,
    ) -> None:
        """Test formatting with zero price."""
        data = RealestateWebhook(
            id="test",
            title="Test",
            price=0,
            currency="IQD",
            area=100,
            city_id=1,
            city_name="Test",
            district_name="Test",
            subdistrict_name="Test",
            category="Test",
            subcategory="Test",
            images=[],
            offer_type="SELL",
            url="https://example.com"
        )

        message = formatter.format(data)

        assert "Price on request" in message


class TestArabicMessageFormatter:
    """Test Arabic message formatting."""

    @pytest.fixture
    def formatter(self) -> ArabicMessageFormatter:
        """Create an Arabic message formatter instance."""
        return ArabicMessageFormatter()

    def test_arabic_price_format(
        self,
        formatter: ArabicMessageFormatter,
    ) -> None:
        """Test Arabic price formatting."""
        data = RealestateWebhook(
            id="test",
            title="Test",
            price=100000,
            currency="IQD",
            area=100,
            city_id=1,
            city_name="Test",
            district_name="Test",
            subdistrict_name="Test",
            category="Test",
            subcategory="Test",
            images=[],
            offer_type="SELL",
            url="https://example.com"
        )

        message = formatter.format(data)

        assert "د.ع" in message

    def test_arabic_link_text(
        self,
        formatter: ArabicMessageFormatter,
    ) -> None:
        """Test Arabic link text."""
        data = RealestateWebhook(
            id="test",
            title="Test",
            price=100000,
            currency="IQD",
            area=100,
            city_id=1,
            city_name="Test",
            district_name="Test",
            subdistrict_name="Test",
            category="Test",
            subcategory="Test",
            images=[],
            offer_type="SELL",
            url="https://example.com"
        )

        message = formatter.format(data)

        assert "عرض التفاصيل" in message
