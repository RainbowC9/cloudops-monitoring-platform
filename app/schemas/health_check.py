from datetime import datetime
from enum import StrEnum
from pydantic import (
    BaseModel,
    ConfigDict,
)

class HealthStatus(StrEnum):
    HEALTHY = "healthy"
    UNHEALTHY = "unhealthy"

class HealthCheckType(StrEnum):
    HTTP = "http"
    TCP = "tcp"

class HealthCheckResponse(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
    )
    id: int
    server_id: int
    service_id: int | None
    check_type: HealthCheckType
    status: HealthStatus
    response_time_ms: float | None
    details: dict | None
    checked_at: datetime

class HealthCheckListResponse(BaseModel):
    items: list[HealthCheckResponse]
    page: int
    page_size: int
    total: int
    total_pages: int

class HealthCheckSummaryResponse(BaseModel):
    total_checks: int
    healthy_checks: int
    unhealthy_checks: int
    monitored_services: int
    by_type: dict[str, int]