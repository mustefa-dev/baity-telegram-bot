from datetime import datetime
from enum import Enum
from typing import Any, Generic, TypeVar

from pydantic import BaseModel, Field


class WebhookStatus(str, Enum):
    """Status of webhook processing."""
    POSTED = "posted"
    SKIPPED = "skipped"
    FAILED = "failed"
    QUEUED = "queued"


class WebhookResponse(BaseModel):
    """Response for webhook endpoints."""
    status: WebhookStatus
    message: str | None = None
    message_id: int | None = Field(default=None, description="Telegram message ID if posted")
    channel_id: str | None = Field(default=None, description="Target channel ID")
    timestamp: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        json_schema_extra = {
            "example": {
                "status": "posted",
                "message": "Successfully posted to Telegram",
                "message_id": 12345,
                "channel_id": "@baghdad_realestate",
                "timestamp": "2024-01-15T10:30:00Z"
            }
        }


class HealthResponse(BaseModel):
    """Response for health check endpoint."""
    status: str = "ok"
    version: str
    environment: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    checks: dict[str, bool] = Field(default_factory=dict)

    class Config:
        json_schema_extra = {
            "example": {
                "status": "ok",
                "version": "1.0.0",
                "environment": "production",
                "timestamp": "2024-01-15T10:30:00Z",
                "checks": {
                    "telegram_bot": True,
                    "configuration": True
                }
            }
        }


class ErrorDetail(BaseModel):
    """Detailed error information."""
    field: str | None = None
    message: str
    code: str | None = None


class ErrorResponse(BaseModel):
    """Standard error response."""
    error: str
    message: str
    details: list[ErrorDetail] | None = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    request_id: str | None = None

    class Config:
        json_schema_extra = {
            "example": {
                "error": "validation_error",
                "message": "Request validation failed",
                "details": [
                    {"field": "price", "message": "Must be greater than 0", "code": "value_error"}
                ],
                "timestamp": "2024-01-15T10:30:00Z",
                "request_id": "req_abc123"
            }
        }


DataT = TypeVar("DataT")


class ApiResponse(BaseModel, Generic[TypeVar("DataT")]):
    """Generic API response wrapper."""
    success: bool
    data: Any | None = None
    error: ErrorResponse | None = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
