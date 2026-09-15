from datetime import datetime
from enum import StrEnum
from urllib.parse import urlparse
from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    model_validator,
)

class ServiceType(StrEnum):
    HTTP = "http"
    TCP = "tcp"

class ServiceStatus(StrEnum):
    UNKNOWN = "unknown"
    HEALTHY = "healthy"
    UNHEALTHY = "unhealthy"

def validate_http_endpoint(value: str) -> str:
    endpoint = value.strip()

    parsed = urlparse(endpoint)

    if parsed.scheme not in {"http", "https"}:
        raise ValueError(
            "HTTP service endpoint must use "
            "http:// or https://."
        )

    if not parsed.hostname:
        raise ValueError(
            "HTTP service endpoint must include a hostname."
        )

    if parsed.username or parsed.password:
        raise ValueError(
            "Credentials must not be embedded in "
            "the monitoring URL."
        )

    return endpoint

def validate_tcp_host(value: str) -> str:
    host = value.strip().lower()

    if not host:
        raise ValueError(
            "TCP service host cannot be empty."
        )

    if "://" in host:
        raise ValueError(
            "TCP endpoints should contain only "
            "a hostname or IP address."
        )

    if "/" in host:
        raise ValueError(
            "TCP endpoint cannot contain a path."
        )
    return host

class ServiceCreate(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        str_strip_whitespace=True,
    )

    server_id: int = Field(
        gt=0,
    )

    name: str = Field(
        min_length=2,
        max_length=100,
    )

    service_type: ServiceType

    endpoint: str = Field(
        min_length=1,
        max_length=500,
    )

    port: int | None = Field(
        default=None,
        ge=1,
        le=65535,
    )
    @model_validator(mode="after")
    def validate_configuration(self):
        if self.service_type == ServiceType.HTTP:
            self.endpoint = validate_http_endpoint(
                self.endpoint
            )
            if self.port is not None:
                raise ValueError(
                    "HTTP services do not require the "
                    "separate port field. Include the port "
                    "inside the URL when needed."
                )
        elif self.service_type == ServiceType.TCP:
            self.endpoint = validate_tcp_host(
                self.endpoint
            )
            if self.port is None:
                raise ValueError(
                    "TCP services require a port."
                )
        return self

class ServiceUpdate(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        str_strip_whitespace=True,
    )

    name: str | None = Field(
        default=None,
        min_length=2,
        max_length=100,
    )

    endpoint: str | None = Field(
        default=None,
        min_length=1,
        max_length=500,
    )

    port: int | None = Field(
        default=None,
        ge=1,
        le=65535,
    )

class ServiceResponse(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
    )
    id: int
    server_id: int

    name: str
    service_type: ServiceType
    endpoint: str | None
    port: int | None
    status: ServiceStatus
    is_active: bool
    created_at: datetime
    updated_at: datetime

class ServiceListResponse(BaseModel):
    items: list[ServiceResponse]
    page: int
    page_size: int
    total: int
    total_pages: int