import pytest
from jwt.exceptions import InvalidTokenError
from app.config import settings
from app.security import (
    create_access_token,
    decode_access_token,
    hash_password,
    verify_password,
)

def test_password_hashing():
    password = "TestingPassword123"

    hashed = hash_password(password)
    assert hashed != password
    assert verify_password(
        password,
        hashed,
    )

    assert not verify_password(
        "WrongPassword123",
        hashed,
    )

def test_access_token_round_trip(
    monkeypatch,
):
    monkeypatch.setattr(
        settings,
        "secret_key",
        (
            "cloudops-test-secret-key-"
            "only-for-pytest"
        ),
    )

    token = create_access_token(
        subject="123"
    )

    payload = decode_access_token(token)

    assert payload["sub"] == "123"


def test_invalid_access_token(
    monkeypatch,
):
    monkeypatch.setattr(
        settings,
        "secret_key",
        (
            "cloudops-test-secret-key-"
            "only-for-pytest"
        ),
    )

    with pytest.raises(
        InvalidTokenError
    ):
        decode_access_token(
            "not-a-valid-jwt"
        )