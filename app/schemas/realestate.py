from enum import Enum
from typing import Annotated

from pydantic import BaseModel, Field, HttpUrl, field_validator


class OfferType(str, Enum):
    """Real estate offer types."""
    SELL = "SELL"
    RENT = "RENT"
    CHALET = "CHALET"


class Currency(str, Enum):
    """Supported currencies."""
    IQD = "IQD"
    USD = "USD"


class RealestateWebhook(BaseModel):
    """Webhook payload for new real estate listings."""

    id: Annotated[str, Field(min_length=1, description="Sqid identifier")]
    title: Annotated[str, Field(min_length=1, max_length=500, description="Listing title")]
    description: Annotated[str | None, Field(max_length=5000, description="Listing description")] = None
    price: Annotated[float, Field(ge=0, description="Price value")]
    currency: Annotated[str, Field(min_length=2, max_length=5, description="Currency code")] = "IQD"
    area: Annotated[float, Field(gt=0, description="Area in square meters")]
    city_id: Annotated[int, Field(gt=0, description="City identifier")]
    city_name: Annotated[str, Field(min_length=1, description="City name")]
    district_name: Annotated[str, Field(min_length=1, description="District name")]
    subdistrict_name: Annotated[str, Field(min_length=1, description="Subdistrict name")]
    category: Annotated[str, Field(min_length=1, description="Category name")]
    subcategory: Annotated[str, Field(min_length=1, description="Subcategory name")]
    images: Annotated[list[str], Field(default_factory=list, description="Image URLs")]
    offer_type: Annotated[str, Field(description="Offer type (SELL, RENT, CHALET)")] = "SELL"
    phone: Annotated[str | None, Field(max_length=20, description="Contact phone number")] = None
    url: Annotated[str, Field(description="Deep link to listing")]
    # Additional specs
    bedrooms: Annotated[int | None, Field(description="Number of bedrooms")] = None
    bathrooms: Annotated[int | None, Field(description="Number of bathrooms")] = None
    floors: Annotated[int | None, Field(description="Number of floors")] = None
    age: Annotated[int | None, Field(description="Property age in years")] = None
    frontage_width: Annotated[float | None, Field(description="Frontage width in meters")] = None
    frontage_depth: Annotated[float | None, Field(description="Frontage depth in meters")] = None

    @field_validator("images", mode="before")
    @classmethod
    def validate_images(cls, v: list[str] | None) -> list[str]:
        """Ensure images is always a list."""
        if v is None:
            return []
        return [img for img in v if img and isinstance(img, str)]

    @field_validator("offer_type", mode="before")
    @classmethod
    def normalize_offer_type(cls, v: str) -> str:
        """Normalize offer type to uppercase."""
        if isinstance(v, str):
            return v.upper()
        return v

    class Config:
        json_schema_extra = {
            "example": {
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
        }
