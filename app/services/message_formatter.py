from typing import Protocol

from app.schemas.realestate import RealestateWebhook


class FormatterProtocol(Protocol):
    """Protocol for message formatters."""

    def format(self, data: RealestateWebhook) -> str:
        """Format data into a message string."""
        ...


class MessageFormatter:
    """Formats real estate data for Telegram messages."""

    # HTML entities for formatting
    OFFER_TYPE_ICONS = {
        "SELL": "For Sale",
        "RENT": "For Rent",
        "CHALET": "Chalet",
    }

    def __init__(
        self,
        max_description_length: int = 200,
        include_phone: bool = True,
    ) -> None:
        self.max_description_length = max_description_length
        self.include_phone = include_phone

    def format(self, data: RealestateWebhook) -> str:
        """Format real estate data into a Telegram message."""
        parts = [
            self._format_title(data.title),
            "",
            self._format_location(data),
            self._format_specs(data),
            self._format_price(data.price, data.currency),
        ]

        if data.description:
            parts.extend(["", self._format_description(data.description)])

        parts.extend([
            "",
            self._format_category(data.category, data.subcategory),
            self._format_offer_type(data.offer_type),
        ])

        if self.include_phone and data.phone:
            parts.append(self._format_phone(data.phone))

        parts.extend(["", self._format_link(data.url)])

        return "\n".join(parts)

    def _format_title(self, title: str) -> str:
        """Format the listing title."""
        # Escape HTML special characters
        escaped = self._escape_html(title)
        return f"<b>{escaped}</b>"

    def _format_location(self, data: RealestateWebhook) -> str:
        """Format location information."""
        location = f"{data.city_name}, {data.district_name}"
        if data.subdistrict_name and data.subdistrict_name != data.district_name:
            location += f", {data.subdistrict_name}"
        return f"{location}"

    def _format_specs(self, data: RealestateWebhook) -> str:
        """Format specifications."""
        return f"{data.area:,.0f} m²"

    def _format_price(self, price: float, currency: str) -> str:
        """Format price with currency."""
        if price <= 0:
            return "Price on request"
        formatted_price = f"{price:,.0f}"
        return f"{formatted_price} {currency}"

    def _format_description(self, description: str) -> str:
        """Format and truncate description."""
        escaped = self._escape_html(description)
        if len(escaped) > self.max_description_length:
            return escaped[:self.max_description_length].rsplit(" ", 1)[0] + "..."
        return escaped

    def _format_category(self, category: str, subcategory: str) -> str:
        """Format category information."""
        return f"{category} - {subcategory}"

    def _format_offer_type(self, offer_type: str) -> str:
        """Format offer type."""
        offer_text = self.OFFER_TYPE_ICONS.get(offer_type.upper(), offer_type)
        return f"{offer_text}"

    def _format_phone(self, phone: str) -> str:
        """Format phone number."""
        return f"Tel: {phone}"

    def _format_link(self, url: str) -> str:
        """Format the link to the listing."""
        return f'<a href="{url}">View Details</a>'

    @staticmethod
    def _escape_html(text: str) -> str:
        """Escape HTML special characters."""
        return (
            text
            .replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
        )


class ArabicMessageFormatter(MessageFormatter):
    """Arabic language formatter for Telegram messages."""

    OFFER_TYPE_ICONS = {
        "SELL": "للبيع",
        "RENT": "للإيجار",
        "CHALET": "شاليه",
    }

    def _format_link(self, url: str) -> str:
        """Format the link to the listing in Arabic."""
        return f'<a href="{url}">عرض التفاصيل</a>'

    def _format_phone(self, phone: str) -> str:
        """Format phone number in Arabic."""
        return f"هاتف: {phone}"

    def _format_price(self, price: float, currency: str) -> str:
        """Format price with currency in Arabic."""
        if price <= 0:
            return "السعر عند الطلب"
        formatted_price = f"{price:,.0f}"
        currency_ar = {"IQD": "د.ع", "USD": "$"}.get(currency, currency)
        return f"{formatted_price} {currency_ar}"
