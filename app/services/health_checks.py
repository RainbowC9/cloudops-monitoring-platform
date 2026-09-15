from dataclasses import dataclass
from ipaddress import ip_address
import socket
from time import perf_counter
from typing import Any
from urllib.parse import urlparse
import httpx
from app.models.service import Service

DEFAULT_TIMEOUT_SECONDS = 5.0

@dataclass(slots=True)
class CheckResult:
    check_type: str
    status: str
    response_time_ms: float | None
    details: dict[str, Any]

def validate_resolved_address(
    address: str,
) -> None:

    parsed = ip_address(address)

    if parsed.is_multicast:
        raise ValueError(
            "Multicast addresses cannot be monitored."
        )
    if parsed.is_unspecified:
        raise ValueError(
            "Unspecified addresses cannot be monitored."
        )
    if parsed.is_link_local:
        raise ValueError(
            "Link-local addresses cannot be monitored."
        )
    if parsed.is_reserved:
        raise ValueError(
            "Reserved addresses cannot be monitored."
        )

def validate_target_host(
    host: str,
    port: int,
) -> None:
    """
    Resolve the target and validate every returned address.
    """

    try:
        results = socket.getaddrinfo(
            host,
            port,
            type=socket.SOCK_STREAM,
        )

    except socket.gaierror as exc:
        raise ValueError(
            "Monitoring target could not be resolved."
        ) from exc

    addresses = {
        item[4][0]
        for item in results
    }

    if not addresses:
        raise ValueError(
            "Monitoring target did not resolve "
            "to an address."
        )

    for address in addresses:
        validate_resolved_address(
            address
        )

def run_http_check(
    endpoint: str,
) -> CheckResult:
    parsed = urlparse(
        endpoint
    )

    if parsed.scheme not in {
        "http",
        "https",
    }:
        raise ValueError(
            "Unsupported HTTP monitoring scheme."
        )

    if parsed.hostname is None:
        raise ValueError(
            "HTTP monitoring target has no hostname."
        )

    port = parsed.port

    if port is None:
        port = (
            443
            if parsed.scheme == "https"
            else 80
        )

    validate_target_host(
        parsed.hostname,
        port,
    )
    started = perf_counter()
    try:
        response = httpx.get(
            endpoint,
            timeout=DEFAULT_TIMEOUT_SECONDS,
            follow_redirects=False,
        )

        elapsed_ms = round(
            (
                perf_counter()
                - started
            )
            * 1000,
            2,
        )

        healthy = (
            200
            <= response.status_code
            < 400
        )

        return CheckResult(
            check_type="http",
            status=(
                "healthy"
                if healthy
                else "unhealthy"
            ),
            response_time_ms=elapsed_ms,
            details={
                "status_code": (
                    response.status_code
                ),
                "target": endpoint,
            },
        )

    except httpx.HTTPError as exc:
        elapsed_ms = round(
            (
                perf_counter()
                - started
            )
            * 1000,
            2,
        )

        return CheckResult(
            check_type="http",
            status="unhealthy",
            response_time_ms=elapsed_ms,
            details={
                "target": endpoint,
                "error_type": (
                    type(exc).__name__
                ),
                "message": str(exc)[:250],
            },
        )

def run_tcp_check(
    host: str,
    port: int,
) -> CheckResult:
    validate_target_host(
        host,
        port,
    )

    started = perf_counter()

    try:
        with socket.create_connection(
            (
                host,
                port,
            ),
            timeout=DEFAULT_TIMEOUT_SECONDS,
        ):
            elapsed_ms = round(
                (
                    perf_counter()
                    - started
                )
                * 1000,
                2,
            )

            return CheckResult(
                check_type="tcp",
                status="healthy",
                response_time_ms=elapsed_ms,
                details={
                    "host": host,
                    "port": port,
                },
            )

    except OSError as exc:
        elapsed_ms = round(
            (
                perf_counter()
                - started
            )
            * 1000,
            2,
        )
        return CheckResult(
            check_type="tcp",
            status="unhealthy",
            response_time_ms=elapsed_ms,
            details={
                "host": host,
                "port": port,
                "error_type": (
                    type(exc).__name__
                ),
                "message": str(exc)[:250],
            },
        )

def run_service_check(
    service: Service,
) -> CheckResult:
    if service.service_type == "http":
        if not service.endpoint:
            raise ValueError(
                "HTTP service has no endpoint."
            )
        return run_http_check(
            service.endpoint
        )

    if service.service_type == "tcp":
        if not service.endpoint:
            raise ValueError(
                "TCP service has no host."
            )

        if service.port is None:
            raise ValueError(
                "TCP service has no port."
            )

        return run_tcp_check(
            service.endpoint,
            service.port,
        )

    raise ValueError(
        "Unsupported service type."
    )