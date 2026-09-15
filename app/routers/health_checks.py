from fastapi import (
    APIRouter,
    HTTPException,
    Query,
    status,
)
from sqlalchemy import (
    distinct,
    func,
    select,
)

from app.dependencies import (
    DatabaseSession,
    EngineerUser,
    ViewerUser,
)
from app.models.audit_log import AuditLog
from app.models.health_check import HealthCheck
from app.models.server import Server
from app.models.service import Service
from app.schemas.health_check import (
    HealthCheckListResponse,
    HealthCheckResponse,
    HealthCheckSummaryResponse,
    HealthCheckType,
    HealthStatus,
)
from app.services.health_checks import (
    run_service_check,
)

router = APIRouter(
    prefix="/api/health-checks",
    tags=["Health Checks"],
)

def get_service_for_check(
    db: DatabaseSession,
    service_id: int,
) -> Service:
    service = db.get(
        Service,
        service_id,
    )
    if service is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Service not found.",
        )
    if not service.is_active:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Service is inactive.",
        )
    server = db.get(
        Server,
        service.server_id,
    )
    if server is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Associated server not found.",
        )
    if not server.is_active:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Associated server is inactive.",
        )
    return service

@router.post(
    "/services/{service_id}/run",
    response_model=HealthCheckResponse,
    status_code=status.HTTP_201_CREATED,
)
def run_health_check(
    service_id: int,
    db: DatabaseSession,
    current_user: EngineerUser,
):

    service = get_service_for_check(
        db,
        service_id,
    )
    try:
        result = run_service_check(
            service
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc
    health_check = HealthCheck(
        server_id=service.server_id,
        service_id=service.id,
        check_type=result.check_type,
        status=result.status,
        response_time_ms=(
            result.response_time_ms
        ),
        details=result.details,
    )
    service.status = result.status
    db.add(
        health_check
    )
    db.flush()
    audit_log = AuditLog(
        user_id=current_user.id,
        action="health_check.executed",
        resource_type="service",
        resource_id=str(
            service.id
        ),
        details={
            "status": result.status,
            "check_type": (
                result.check_type
            ),
            "response_time_ms": (
                result.response_time_ms
            ),
        },
    )
    db.add(
        audit_log
    )
    db.commit()
    db.refresh(
        health_check
    )

    return health_check

@router.get(
    "",
    response_model=HealthCheckListResponse,
)
def list_health_checks(
    db: DatabaseSession,
    current_user: ViewerUser,
    page: int = Query(
        default=1,
        ge=1,
    ),
    page_size: int = Query(
        default=20,
        ge=1,
        le=100,
    ),
    server_id: int | None = Query(
        default=None,
        gt=0,
    ),
    service_id: int | None = Query(
        default=None,
        gt=0,
    ),
    check_type: HealthCheckType | None = None,
    health_status: HealthStatus | None = Query(
        default=None,
        alias="status",
    ),
):
    filters = []
    if server_id is not None:
        filters.append(
            HealthCheck.server_id
            == server_id
        )
    if service_id is not None:
        filters.append(
            HealthCheck.service_id
            == service_id
        )
    if check_type is not None:
        filters.append(
            HealthCheck.check_type
            == check_type.value
        )
    if health_status is not None:
        filters.append(
            HealthCheck.status
            == health_status.value
        )
    total = int(
        db.scalar(
            select(
                func.count(
                    HealthCheck.id
                )
            ).where(
                *filters
            )
        )
        or 0
    )
    offset = (
        page - 1
    ) * page_size

    statement = (
        select(HealthCheck)
        .where(
            *filters
        )
        .order_by(
            HealthCheck.checked_at.desc(),
            HealthCheck.id.desc(),
        )
        .offset(offset)
        .limit(page_size)
    )
    items = list(
        db.scalars(
            statement
        ).all()
    )
    total_pages = (
        (
            total
            + page_size
            - 1
        )
        // page_size
        if total > 0
        else 0
    )
    return HealthCheckListResponse(
        items=items,
        page=page,
        page_size=page_size,
        total=total,
        total_pages=total_pages,
    )

@router.get(
    "/summary",
    response_model=HealthCheckSummaryResponse,
)
def health_check_summary(
    db: DatabaseSession,
    current_user: ViewerUser,
):
    total_checks = int(
        db.scalar(
            select(
                func.count(
                    HealthCheck.id
                )
            )
        )
        or 0
    )

    healthy_checks = int(
        db.scalar(
            select(
                func.count(
                    HealthCheck.id
                )
            ).where(
                HealthCheck.status
                == "healthy"
            )
        )
        or 0
    )

    unhealthy_checks = int(
        db.scalar(
            select(
                func.count(
                    HealthCheck.id
                )
            ).where(
                HealthCheck.status
                == "unhealthy"
            )
        )
        or 0
    )

    monitored_services = int(
        db.scalar(
            select(
                func.count(
                    distinct(
                        HealthCheck.service_id
                    )
                )
            ).where(
                HealthCheck.service_id
                .is_not(None)
            )
        )
        or 0
    )

    type_rows = db.execute(
        select(
            HealthCheck.check_type,
            func.count(
                HealthCheck.id
            ),
        ).group_by(
            HealthCheck.check_type
        )
    ).all()

    by_type = {
        check_type: count
        for check_type, count
        in type_rows
    }

    return HealthCheckSummaryResponse(
        total_checks=total_checks,
        healthy_checks=healthy_checks,
        unhealthy_checks=unhealthy_checks,
        monitored_services=monitored_services,
        by_type=by_type,
    )

@router.get(
    "/services/{service_id}/latest",
    response_model=HealthCheckResponse,
)
def latest_service_health_check(
    service_id: int,
    db: DatabaseSession,
    current_user: ViewerUser,
):
    service = db.get(
        Service,
        service_id,
    )

    if service is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Service not found.",
        )

    statement = (
        select(HealthCheck)
        .where(
            HealthCheck.service_id
            == service_id
        )
        .order_by(
            HealthCheck.checked_at.desc(),
            HealthCheck.id.desc(),
        )
        .limit(1)
    )

    health_check = db.scalar(
        statement
    )

    if health_check is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=(
                "No health checks have been "
                "recorded for this service."
            ),
        )

    return health_check