from enum import Enum
from fastapi import (APIRouter, HTTPException, Query, status,)
from sqlalchemy import (func, or_, select,)
from sqlalchemy.exc import IntegrityError
from app.dependencies import (AdminUser, DatabaseSession, EngineerUser, ViewerUser, )
from app.models.audit_log import AuditLog
from app.models.server import Server
from app.schemas.server import ( ServerCreate, ServerEnvironment, ServerListResponse, ServerResponse, ServerStatus, ServerSummaryResponse, ServerUpdate,)

router = APIRouter(
    prefix="/api/servers",
    tags=["Servers"],
)

def enum_value(value):
    if isinstance(value, Enum):
        return value.value

    return value

def get_server_or_404(
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

    return server

def ensure_unique_server_identity(
    db: DatabaseSession,
    *,
    name: str,
    hostname: str,
    exclude_server_id: int | None = None,
) -> None:
    statement = select(Server).where(
        or_(
            func.lower(Server.name)
            == name.lower(),
            func.lower(Server.hostname)
            == hostname.lower(),
        )
    )

    if exclude_server_id is not None:
        statement = statement.where(
            Server.id != exclude_server_id
        )

    existing = db.scalar(statement)

    if existing is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "A server with this name or "
                "hostname already exists."
            ),
        )

def add_audit_log(
    db: DatabaseSession,
    *,
    user_id: int,
    action: str,
    server_id: int,
    details: dict | None = None,
) -> None:
    audit_log = AuditLog(
        user_id=user_id,
        action=action,
        resource_type="server",
        resource_id=str(server_id),
        details=details,
    )

    db.add(audit_log)

@router.post(
    "",
    response_model=ServerResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_server(
    payload: ServerCreate,
    db: DatabaseSession,
    current_user: EngineerUser,
):

    ensure_unique_server_identity(
        db,
        name=payload.name,
        hostname=payload.hostname,
    )

    server = Server(
        name=payload.name,
        hostname=payload.hostname,
        ip_address=payload.ip_address,
        environment=payload.environment.value,
        operating_system=payload.operating_system,
        status=payload.status.value,
        is_active=True,
    )

    try:
        db.add(server)
        db.flush()

        add_audit_log(
            db,
            user_id=current_user.id,
            action="server.created",
            server_id=server.id,
            details={
                "name": server.name,
                "hostname": server.hostname,
                "ip_address": server.ip_address,
                "environment": server.environment,
            },
        )

        db.commit()
        db.refresh(server)

    except IntegrityError as exc:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "A server with this name or "
                "hostname already exists."
            ),
        ) from exc

    return server

@router.get(
    "",
    response_model=ServerListResponse,
)
def list_servers(
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
    search: str | None = Query(
        default=None,
        min_length=1,
        max_length=100,
    ),
    environment: ServerEnvironment | None = None,
    server_status: ServerStatus | None = Query(
        default=None,
        alias="status",
    ),
    include_inactive: bool = False,
):

    filters = []

    if not include_inactive:
        filters.append(
            Server.is_active.is_(True)
        )

    if environment is not None:
        filters.append(
            Server.environment
            == environment.value
        )

    if server_status is not None:
        filters.append(
            Server.status
            == server_status.value
        )

    if search is not None:
        search_value = search.strip()

        if search_value:
            pattern = f"%{search_value}%"

            filters.append(
                or_(
                    Server.name.ilike(pattern),
                    Server.hostname.ilike(pattern),
                    Server.ip_address.ilike(pattern),
                )
            )

    count_statement = (
        select(
            func.count(Server.id)
        )
        .where(
            *filters
        )
    )

    total = int(
        db.scalar(
            count_statement
        )
        or 0
    )

    offset = (
        page - 1
    ) * page_size

    statement = (
        select(Server)
        .where(
            *filters
        )
        .order_by(
            Server.name.asc()
        )
        .offset(offset)
        .limit(page_size)
    )

    servers = list(
        db.scalars(
            statement
        ).all()
    )

    total_pages = (
        (total + page_size - 1)
        // page_size
        if total > 0
        else 0
    )

    return ServerListResponse(
        items=servers,
        page=page,
        page_size=page_size,
        total=total,
        total_pages=total_pages,
    )


@router.get(
    "/summary",
    response_model=ServerSummaryResponse,
)
def server_summary(
    db: DatabaseSession,
    current_user: ViewerUser,
):

    total = int(
        db.scalar(
            select(
                func.count(Server.id)
            )
        )
        or 0
    )

    active = int(
        db.scalar(
            select(
                func.count(Server.id)
            ).where(
                Server.is_active.is_(True)
            )
        )
        or 0
    )

    inactive = total - active

    status_rows = db.execute(
        select(
            Server.status,
            func.count(Server.id),
        )
        .where(
            Server.is_active.is_(True)
        )
        .group_by(
            Server.status
        )
    ).all()

    environment_rows = db.execute(
        select(
            Server.environment,
            func.count(Server.id),
        )
        .where(
            Server.is_active.is_(True)
        )
        .group_by(
            Server.environment
        )
    ).all()

    by_status = {
        status_name: count
        for status_name, count
        in status_rows
    }

    by_environment = {
        environment_name: count
        for environment_name, count
        in environment_rows
    }

    return ServerSummaryResponse(
        total=total,
        active=active,
        inactive=inactive,
        by_status=by_status,
        by_environment=by_environment,
    )


@router.get(
    "/{server_id}",
    response_model=ServerResponse,
)
def get_server(
    server_id: int,
    db: DatabaseSession,
    current_user: ViewerUser,
):

    return get_server_or_404(
        db,
        server_id,
    )

@router.put(
    "/{server_id}",
    response_model=ServerResponse,
)
def update_server(
    server_id: int,
    payload: ServerUpdate,
    db: DatabaseSession,
    current_user: EngineerUser,
):

    server = get_server_or_404(
        db,
        server_id,
    )

    updates = payload.model_dump(
        exclude_unset=True
    )

    if not updates:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "At least one field must be "
                "provided for update."
            ),
        )

    candidate_name = (
        updates.get(
            "name",
            server.name,
        )
    )

    candidate_hostname = (
        updates.get(
            "hostname",
            server.hostname,
        )
    )

    ensure_unique_server_identity(
        db,
        name=candidate_name,
        hostname=candidate_hostname,
        exclude_server_id=server.id,
    )

    changes = {}

    for field_name, new_value in updates.items():
        new_value = enum_value(
            new_value
        )

        old_value = getattr(
            server,
            field_name,
        )

        if old_value != new_value:
            changes[field_name] = {
                "from": old_value,
                "to": new_value,
            }

            setattr(
                server,
                field_name,
                new_value,
            )

    if not changes:
        return server

    try:
        db.flush()

        add_audit_log(
            db,
            user_id=current_user.id,
            action="server.updated",
            server_id=server.id,
            details={
                "changes": changes,
            },
        )

        db.commit()
        db.refresh(server)

    except IntegrityError as exc:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "A server with this name or "
                "hostname already exists."
            ),
        ) from exc

    return server

@router.patch(
    "/{server_id}/deactivate",
    response_model=ServerResponse,
)
def deactivate_server(
    server_id: int,
    db: DatabaseSession,
    current_user: AdminUser,
):

    server = get_server_or_404(
        db,
        server_id,
    )

    if not server.is_active:
        return server

    server.is_active = False

    add_audit_log(
        db,
        user_id=current_user.id,
        action="server.deactivated",
        server_id=server.id,
        details={
            "name": server.name,
            "hostname": server.hostname,
        },
    )
    db.commit()
    db.refresh(server)

    return server