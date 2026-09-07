from datetime import datetime, timedelta, timezone
import jwt
from pwdlib import PasswordHash
from app.config import settings

password_hasher = PasswordHash.recommended()

def hash_password(password: str) -> str:
    return password_hasher.hash(password)

def verify_password(
    plain_password: str,
    hashed_password: str,
) -> bool:

    return password_hasher.verify(
        plain_password,
        hashed_password,
    )

def get_secret_key() -> str:

    if not settings.secret_key:
        raise RuntimeError(
            "SECRET_KEY is not configured. "
            "Add it to the local .env file."
        )

    return settings.secret_key

def create_access_token(
    subject: str,
    expires_delta: timedelta | None = None,
) -> str:

    if expires_delta is None:
        expires_delta = timedelta(
            minutes=settings.access_token_expire_minutes
        )

    expires_at = (
        datetime.now(timezone.utc)
        + expires_delta
    )

    payload = {
        "sub": subject,
        "exp": expires_at,
        "iat": datetime.now(timezone.utc),
    }

    return jwt.encode(
        payload,
        get_secret_key(),
        algorithm=settings.jwt_algorithm,
    )

def decode_access_token(token: str) -> dict:
    return jwt.decode(
        token,
        get_secret_key(),
        algorithms=[settings.jwt_algorithm],
    )