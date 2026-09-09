from getpass import getpass
from sqlalchemy import select
from sqlalchemy.orm import joinedload
from app.database import SessionLocal
from app.models.user import User
from app.security import hash_password

def reset_admin_password() -> None:
    if SessionLocal is None:
        raise RuntimeError(
            "DATABASE_URL is not configured."
        )

    username = input(
        "Admin username or email: "
    ).strip()

    if not username:
        raise ValueError(
            "Username or email cannot be empty."
        )

    new_password = getpass(
        "New password (minimum 12 characters): "
    )

    if len(new_password) < 12:
        raise ValueError(
            "Password must contain at least 12 characters."
        )

    confirmation = getpass(
        "Confirm new password: "
    )

    if new_password != confirmation:
        raise ValueError(
            "Passwords do not match."
        )

    with SessionLocal() as db:
        statement = (
            select(User)
            .options(
                joinedload(User.role)
            )
            .where(
                (User.username == username)
                | (User.email == username.lower())
            )
        )

        user = db.scalar(statement)

        if user is None:
            raise RuntimeError(
                "User not found."
            )

        if user.role is None or user.role.name != "Admin":
            raise RuntimeError(
                "The selected user is not an Admin."
            )

        user.password_hash = hash_password(
            new_password
        )

        db.commit()

        print()
        print(
            "Admin password updated successfully."
        )
        print(
            f"Username: {user.username}"
        )
        print(
            f"Email: {user.email}"
        )

if __name__ == "__main__":
    reset_admin_password()