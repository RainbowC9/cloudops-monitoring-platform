from datetime import (
    datetime,
    timezone,
)

from fastapi import (
    APIRouter,
    HTTPException,
    Response,
    status,
)

from app.dependencies import (
    DatabaseSession,
    ViewerUser,
)
from app.models.server import Server
from app.schemas.metrics import (
    DiskMetricsResponse,
    DiskUsageItem,
    MetricValueResponse,
    PrometheusHealthResponse,
    ServerMetricsOverviewResponse,
)
from app.services.prometheus import (
    PrometheusQueryError,
    prometheus_client,
)


router = APIRouter(
    prefix="/api/metrics",
    tags=["Infrastructure Metrics"],
)


def get_active_server(
    db: DatabaseSession,
    server_id: int,
) -> Server:
    server = db.get(
        Server,
        server_id,
    )

    if server is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Server not found.",
        )

    if not server.is_active:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Server is inactive.",
        )

    return server


def get_instance(
    server: Server,
) -> str:
    try:
        return (
            prometheus_client
            .build_windows_instance(
                server.ip_address
            )
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "Server does not contain a valid "
                "IP address for metrics lookup."
            ),
        ) from exc


def prometheus_unavailable(
    exc: PrometheusQueryError,
) -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        detail=str(exc),
    )


@router.get(
    "/health",
    response_model=PrometheusHealthResponse,
)
def metrics_health(
    response: Response,
    current_user: ViewerUser,
):
    try:
        prometheus_client.health()

    except PrometheusQueryError:
        response.status_code = (
            status.HTTP_503_SERVICE_UNAVAILABLE
        )

        return PrometheusHealthResponse(
            status="unavailable",
            url=prometheus_client.base_url,
        )

    return PrometheusHealthResponse(
        status="healthy",
        url=prometheus_client.base_url,
    )


@router.get(
    "/servers/{server_id}/cpu",
    response_model=MetricValueResponse,
)
def server_cpu(
    server_id: int,
    db: DatabaseSession,
    current_user: ViewerUser,
):
    server = get_active_server(
        db,
        server_id,
    )

    instance = get_instance(
        server
    )

    try:
        value = prometheus_client.cpu_percent(
            instance
        )

    except PrometheusQueryError as exc:
        raise prometheus_unavailable(
            exc
        ) from exc

    return MetricValueResponse(
        server_id=server.id,
        server_name=server.name,
        instance=instance,
        metric="cpu_usage",
        value=value,
        unit="percent",
        available=value is not None,
    )


@router.get(
    "/servers/{server_id}/memory",
    response_model=MetricValueResponse,
)
def server_memory(
    server_id: int,
    db: DatabaseSession,
    current_user: ViewerUser,
):
    server = get_active_server(
        db,
        server_id,
    )

    instance = get_instance(
        server
    )

    try:
        value = (
            prometheus_client
            .memory_percent(
                instance
            )
        )

    except PrometheusQueryError as exc:
        raise prometheus_unavailable(
            exc
        ) from exc

    return MetricValueResponse(
        server_id=server.id,
        server_name=server.name,
        instance=instance,
        metric="memory_usage",
        value=value,
        unit="percent",
        available=value is not None,
    )


@router.get(
    "/servers/{server_id}/disk",
    response_model=DiskMetricsResponse,
)
def server_disk(
    server_id: int,
    db: DatabaseSession,
    current_user: ViewerUser,
):
    server = get_active_server(
        db,
        server_id,
    )

    instance = get_instance(
        server
    )

    try:
        disks = (
            prometheus_client
            .disk_usage(
                instance
            )
        )

    except PrometheusQueryError as exc:
        raise prometheus_unavailable(
            exc
        ) from exc

    return DiskMetricsResponse(
        server_id=server.id,
        server_name=server.name,
        instance=instance,
        disks=[
            DiskUsageItem(
                **disk
            )
            for disk in disks
        ],
    )


@router.get(
    "/servers/{server_id}/overview",
    response_model=ServerMetricsOverviewResponse,
)
def server_metrics_overview(
    server_id: int,
    db: DatabaseSession,
    current_user: ViewerUser,
):
    server = get_active_server(
        db,
        server_id,
    )

    instance = get_instance(
        server
    )

    try:
        cpu_percent = (
            prometheus_client
            .cpu_percent(
                instance
            )
        )

        memory_percent = (
            prometheus_client
            .memory_percent(
                instance
            )
        )

        disk_results = (
            prometheus_client
            .disk_usage(
                instance
            )
        )

    except PrometheusQueryError as exc:
        raise prometheus_unavailable(
            exc
        ) from exc

    disks = [
        DiskUsageItem(
            **disk
        )
        for disk in disk_results
    ]

    return ServerMetricsOverviewResponse(
        server_id=server.id,
        server_name=server.name,
        instance=instance,
        cpu_percent=cpu_percent,
        memory_percent=memory_percent,
        disks=disks,
        collected_at=datetime.now(
            timezone.utc
        ),
    )