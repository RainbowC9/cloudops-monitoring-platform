from fastapi import (
    APIRouter,
    HTTPException,
    Query,
    status,
)
from sqlalchemy import (
    func,
    select,
)
from sqlalchemy.exc import IntegrityError
from app.dependencies import (
    AdminUser,
    DatabaseSession,
    EngineerUser,
    ViewerUser,
)
from app.models.audit_log import AuditLog
from app.models.server import Server
from app.models.service import Service
from app.schemas.service import (
    ServiceCreate,
    ServiceListResponse,
    ServiceResponse,
    ServiceStatus,
    ServiceType,
    ServiceUpdate,
)

router = APIRouter(
    prefix="/api/services",
    tags=["Services"],
)

def get_service_or_404(
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

    return service

def get_active_server_or_404(
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
            detail=(
                "Cannot register a service "
                "against an inactive server."
            ),
        )

    return server

def ensure_unique_service_name(
    db: DatabaseSession,
    *,
    server_id: int,
    name: str,
    exclude_service_id: int | None = None,
) -> None:
    statement = select(
        Service
    ).where(
        Service.server_id == server_id,
        func.lower(Service.name)
        == name.lower(),
    )

    if exclude_service_id is not None:
        statement = statement.where(
            Service.id
            != exclude_service_id
        )

    existing = db.scalar(
        statement
    )

    if existing is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "A service with this name "
                "already exists on this server."
            ),
        )

def add_service_audit_log(
    db: DatabaseSession,
    *,
    user_id: int,
    action: str,
    service_id: int,
    details: dict | None = None,
) -> None:
    log = AuditLog(
        user_id=user_id,
        action=action,
        resource_type="service",
        resource_id=str(service_id),
        details=details,
    )

    db.add(log)

@router.post(
    "",
    response_model=ServiceResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_service(
    payload: ServiceCreate,
    db: DatabaseSession,
    current_user: EngineerUser,
):
    get_active_server_or_404(
        db,
        payload.server_id,
    )

    ensure_unique_service_name(
        db,
        server_id=payload.server_id,
        name=payload.name,
    )

    service = Service(
        server_id=payload.server_id,
        name=payload.name,
        service_type=(
            payload.service_type.value
        ),
        endpoint=payload.endpoint,
        port=payload.port,
        status="unknown",
        is_active=True,
    )

    try:
        db.add(service)
        db.flush()

        add_service_audit_log(
            db,
            user_id=current_user.id,
            action="service.created",
            service_id=service.id,
            details={
                "name": service.name,
                "type": service.service_type,
                "server_id": service.server_id,
            },
        )

        db.commit()
        db.refresh(service)

    except IntegrityError as exc:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "A service with this name "
                "already exists on this server."
            ),
        ) from exc

    return service

@router.get(
    "",
    response_model=ServiceListResponse,
)
def list_services(
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
    service_type: ServiceType | None = None,
    service_status: ServiceStatus | None = Query(
        default=None,
        alias="status",
    ),
    search: str | None = Query(
        default=None,
        min_length=1,
        max_length=100,
    ),
    include_inactive: bool = False,
):
    filters = []

    if not include_inactive:
        filters.append(
            Service.is_active.is_(True)
        )

    if server_id is not None:
        filters.append(
            Service.server_id
            == server_id
        )

    if service_type is not None:
        filters.append(
            Service.service_type
            == service_type.value
        )

    if service_status is not None:
        filters.append(
            Service.status
            == service_status.value
        )

    if search is not None:
        pattern = (
            f"%{search.strip()}%"
        )

        filters.append(
            Service.name.ilike(
                pattern
            )
        )

    total = int(
        db.scalar(
            select(
                func.count(
                    Service.id
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
        select(Service)
        .where(
            *filters
        )
        .order_by(
            Service.name.asc()
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

    return ServiceListResponse(
        items=items,
        page=page,
        page_size=page_size,
        total=total,
        total_pages=total_pages,
    )

@router.get(
    "/{service_id}",
    response_model=ServiceResponse,
)
def get_service(
    service_id: int,
    db: DatabaseSession,
    current_user: ViewerUser,
):
    return get_service_or_404(
        db,
        service_id,
    )

@router.put(
    "/{service_id}",
    response_model=ServiceResponse,
)
def update_service(
    service_id: int,
    payload: ServiceUpdate,
    db: DatabaseSession,
    current_user: EngineerUser,
):
    service = get_service_or_404(
        db,
        service_id,
    )

    updates = payload.model_dump(
        exclude_unset=True
    )

    if not updates:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "At least one field must "
                "be provided."
            ),
        )

    candidate_name = updates.get(
        "name",
        service.name,
    )

    candidate_endpoint = updates.get(
        "endpoint",
        service.endpoint,
    )

    candidate_port = updates.get(
        "port",
        service.port,
    )

    validation_payload = ServiceCreate(
        server_id=service.server_id,
        name=candidate_name,
        service_type=service.service_type,
        endpoint=candidate_endpoint,
        port=candidate_port,
    )

    ensure_unique_service_name(
        db,
        server_id=service.server_id,
        name=validation_payload.name,
        exclude_service_id=service.id,
    )
    changes = {}

    for field_name in (
        "name",
        "endpoint",
        "port",
    ):
        new_value = getattr(
            validation_payload,
            field_name,
        )

        old_value = getattr(
            service,
            field_name,
        )

        if old_value != new_value:
            changes[field_name] = {
                "from": old_value,
                "to": new_value,
            }
            setattr(
                service,
                field_name,
                new_value,
            )

    if not changes:
        return service
    try:
        db.flush()

        add_service_audit_log(
            db,
            user_id=current_user.id,
            action="service.updated",
            service_id=service.id,
            details={
                "changes": changes,
            },
        )
        db.commit()
        db.refresh(service)

    except IntegrityError as exc:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "A service with this name "
                "already exists on this server."
            ),
        ) from exc
    return service

@router.patch(
    "/{service_id}/deactivate",
    response_model=ServiceResponse,
)
def deactivate_service(
    service_id: int,
    db: DatabaseSession,
    current_user: AdminUser,
):
    service = get_service_or_404(
        db,
        service_id,
    )

    if not service.is_active:
        return service
    service.is_active = False
    add_service_audit_log(
        db,
        user_id=current_user.id,
        action="service.deactivated",
        service_id=service.id,
        details={
            "name": service.name,
            "server_id": service.server_id,
        },
    )
    db.commit()
    db.refresh(service)

    return service