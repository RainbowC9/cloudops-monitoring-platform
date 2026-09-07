from getpass import getpass
from sqlalchemy import or_, select
from app.database import SessionLocal
from app.models.role import Role
from app.models.user import User
from app.security import hash_password


def prompt_required(label: str) -> str:
    while True:
        value = input(label).strip()

        if value:
            return value

        print("This value cannot be empty.")

def create_admin() -> None:
    if SessionLocal is None:
        raise RuntimeError(
            "DATABASE_URL is not configured."
        )

    print()
    print("CloudOps Initial Admin Setup")
    print("----------------------------")

    username = prompt_required(
        "Username: "
    )

    email = prompt_required(
        "Email: "
    ).lower()

    if "@" not in email:
        raise ValueError(
            "Please enter a valid email address."
        )

    password = getpass(
        "Password (minimum 12 characters): "
    )

    if len(password) < 12:
        raise ValueError(
            "Admin password must contain "
            "at least 12 characters."
        )

    confirmation = getpass(
        "Confirm password: "
    )

    if password != confirmation:
        raise ValueError(
            "Passwords do not match."
        )

    with SessionLocal() as db:

        admin_role = db.scalar(
            select(Role).where(
                Role.name == "Admin"
            )
        )

        if admin_role is None:
            raise RuntimeError(
                "Admin role does not exist. "
                "Run: python -m scripts.seed_roles"
            )

        existing_user = db.scalar(
            select(User).where(
                or_(
                    User.username == username,
                    User.email == email,
                )
            )
        )

        if existing_user is not None:
            raise RuntimeError(
                "A user with this username "
                "or email already exists."
            )

        admin = User(
            role_id=admin_role.id,
            username=username,
            email=email,
            password_hash=hash_password(
                password
            ),
            is_active=True,
        )

        db.add(admin)
        db.commit()
        db.refresh(admin)

        print()
        print(
            "CloudOps Admin created successfully."
        )
        print(
            f"User ID: {admin.id}"
        )
        print(
            f"Username: {admin.username}"
        )
        print(
            f"Email: {admin.email}"
        )

if __name__ == "__main__":
    create_admin()