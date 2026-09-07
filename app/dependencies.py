from typing import Annotated
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jwt.exceptions import InvalidTokenError
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload
from app.database import get_db
from app.models.user import User
from app.security import decode_access_token

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/api/auth/login"
)

DatabaseSession = Annotated[
    Session,
    Depends(get_db),
]

AccessToken = Annotated[
    str,
    Depends(oauth2_scheme),
]

def get_current_user(
    token: AccessToken,
    db: DatabaseSession,
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate authentication credentials.",
        headers={
            "WWW-Authenticate": "Bearer",
        },
    )

    try:
        payload = decode_access_token(token)
        subject = payload.get("sub")

        if subject is None:
            raise credentials_exception

        user_id = int(subject)

    except (InvalidTokenError, ValueError):
        raise credentials_exception

    statement = (
        select(User)
        .options(
            joinedload(User.role)
        )
        .where(
            User.id == user_id
        )
    )

    user = db.scalar(statement)

    if user is None:
        raise credentials_exception

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive.",
        )
    return user

CurrentUser = Annotated[
    User,
    Depends(get_current_user),
]

def require_roles(*allowed_roles: str):
    def role_checker(
        current_user: CurrentUser,
    ) -> User:
        if (
            current_user.role is None
            or current_user.role.name not in allowed_roles
        ):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=(
                    "You do not have permission "
                    "to access this resource."
                ),
            )
        return current_user
    return role_checker

AdminUser = Annotated[
    User,
    Depends(
        require_roles(
            "Admin",
        )
    ),
]

EngineerUser = Annotated[
    User,
    Depends(
        require_roles(
            "Admin",
            "Engineer",
        )
    ),
]

ViewerUser = Annotated[
    User,
    Depends(
        require_roles(
            "Admin",
            "Engineer",
            "Viewer",
        )
    ),
]