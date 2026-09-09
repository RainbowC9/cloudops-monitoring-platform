from datetime import datetime
from enum import StrEnum
from ipaddress import ip_address
from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    field_validator,
)

class ServerEnvironment(StrEnum):
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"

class ServerStatus(StrEnum):
    UNKNOWN = "unknown"
    ONLINE = "online"
    OFFLINE = "offline"
    WARNING = "warning"
    CRITICAL = "critical"
    MAINTENANCE = "maintenance"

def validate_ip_address(value: str) -> str:
    try:
        return str(ip_address(value))
    except ValueError as exc:
        raise ValueError(
            "A valid IPv4 or IPv6 address is required."
        ) from exc

def validate_hostname(value: str) -> str:
    hostname = value.strip().lower()

    if not hostname:
        raise ValueError(
            "Hostname cannot be empty."
        )

    if len(hostname) > 253:
        raise ValueError(
            "Hostname cannot exceed 253 characters."
        )

    allowed_characters = set(
        "abcdefghijklmnopqrstuvwxyz"
        "0123456789-."
    )

    if any(
        character not in allowed_characters
        for character in hostname
    ):
        raise ValueError(
            "Hostname may contain only letters, "
            "numbers, hyphens, and dots."
        )

    labels = hostname.split(".")

    for label in labels:
        if not label:
            raise ValueError(
                "Hostname contains an empty label."
            )

        if label.startswith("-") or label.endswith("-"):
            raise ValueError(
                "Hostname labels cannot start or end "
                "with a hyphen."
            )

        if len(label) > 63:
            raise ValueError(
                "Each hostname label must be "
                "63 characters or fewer."
            )

    return hostname

def normalize_optional_text(
    value: str | None,
) -> str | None:
    if value is None:
        return None

    value = value.strip()

    return value or None


class ServerCreate(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        str_strip_whitespace=True,
    )

    name: str = Field(
        min_length=2,
        max_length=100,
    )

    hostname: str = Field(
        min_length=1,
        max_length=255,
    )

    ip_address: str

    environment: ServerEnvironment = (
        ServerEnvironment.DEVELOPMENT
    )

    operating_system: str | None = Field(
        default=None,
        max_length=150,
    )

    status: ServerStatus = ServerStatus.UNKNOWN

    @field_validator("hostname")
    @classmethod
    def validate_server_hostname(
        cls,
        value: str,
    ) -> str:
        return validate_hostname(value)

    @field_validator("ip_address")
    @classmethod
    def validate_server_ip(
        cls,
        value: str,
    ) -> str:
        return validate_ip_address(value)

    @field_validator("operating_system")
    @classmethod
    def normalize_operating_system(
        cls,
        value: str | None,
    ) -> str | None:
        return normalize_optional_text(value)


class ServerUpdate(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        str_strip_whitespace=True,
    )

    name: str | None = Field(
        default=None,
        min_length=2,
        max_length=100,
    )

    hostname: str | None = Field(
        default=None,
        min_length=1,
        max_length=255,
    )

    ip_address: str | None = None

    environment: ServerEnvironment | None = None

    operating_system: str | None = Field(
        default=None,
        max_length=150,
    )

    status: ServerStatus | None = None

    @field_validator("hostname")
    @classmethod
    def validate_server_hostname(
        cls,
        value: str | None,
    ) -> str | None:
        if value is None:
            return None

        return validate_hostname(value)

    @field_validator("ip_address")
    @classmethod
    def validate_server_ip(
        cls,
        value: str | None,
    ) -> str | None:
        if value is None:
            return None

        return validate_ip_address(value)

    @field_validator("operating_system")
    @classmethod
    def normalize_operating_system(
        cls,
        value: str | None,
    ) -> str | None:
        return normalize_optional_text(value)

class ServerResponse(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
    )

    id: int
    name: str
    hostname: str
    ip_address: str
    environment: ServerEnvironment
    operating_system: str | None
    status: ServerStatus
    is_active: bool
    created_at: datetime
    updated_at: datetime

class ServerListResponse(BaseModel):
    items: list[ServerResponse]

    page: int
    page_size: int

    total: int
    total_pages: int

class ServerSummaryResponse(BaseModel):
    total: int
    active: int
    inactive: int

    by_status: dict[str, int]

    by_environment: dict[str, int]