from typing import Annotated
from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
)
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import or_, select
from sqlalchemy.orm import Session, joinedload
from app.config import settings
from app.database import get_db
from app.dependencies import (
    AdminUser,
    CurrentUser,
    EngineerUser,
    ViewerUser,
)
from app.models.user import User
from app.schemas.auth import (
    AccessResponse,
    TokenResponse,
    UserResponse,
)
from app.security import (
    create_access_token,
    verify_password,
)

router = APIRouter(
    prefix="/api/auth",
    tags=["Authentication"],
)


@router.post(
    "/login",
    response_model=TokenResponse,
)
def login(
    form_data: Annotated[
        OAuth2PasswordRequestForm,
        Depends(),
    ],
    db: Annotated[
        Session,
        Depends(get_db),
    ],
):

    login_value = form_data.username.strip()

    statement = (
        select(User)
        .options(
            joinedload(User.role)
        )
        .where(
            or_(
                User.username == login_value,
                User.email == login_value.lower(),
            )
        )
    )
    user = db.scalar(statement)

    if (
        user is None
        or not verify_password(
            form_data.password,
            user.password_hash,
        )
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username/email or password.",
            headers={
                "WWW-Authenticate": "Bearer",
            },
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive.",
        )

    access_token = create_access_token(
        subject=str(user.id)
    )

    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        expires_in=(
            settings.access_token_expire_minutes
            * 60
        ),
    )

@router.get(
    "/me",
    response_model=UserResponse,
)
def get_my_profile(
    current_user: CurrentUser,
):

    return UserResponse(
        id=current_user.id,
        username=current_user.username,
        email=current_user.email,
        role=current_user.role.name,
        is_active=current_user.is_active,
    )

@router.get(
    "/access/viewer",
    response_model=AccessResponse,
)
def viewer_access(
    current_user: ViewerUser,
):

    return AccessResponse(
        message="Viewer access granted.",
        username=current_user.username,
        role=current_user.role.name,
    )

@router.get(
    "/access/engineer",
    response_model=AccessResponse,
)
def engineer_access(
    current_user: EngineerUser,
):

    return AccessResponse(
        message="Engineer access granted.",
        username=current_user.username,
        role=current_user.role.name,
    )

@router.get(
    "/access/admin",
    response_model=AccessResponse,
)
def admin_access(
    current_user: AdminUser,
):
    return AccessResponse(
        message="Admin access granted.",
        username=current_user.username,
        role=current_user.role.name,
    )