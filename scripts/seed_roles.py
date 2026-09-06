from sqlalchemy import select
from app.database import SessionLocal
from app.models.role import Role


DEFAULT_ROLES = [
    {
        "name": "Admin",
        "description": (
            "Full administrative access to CloudOps."
        ),
    },
    {
        "name": "Engineer",
        "description": (
            "Operational access for monitoring "
            "and incident management."
        ),
    },
    {
        "name": "Viewer",
        "description": (
            "Read-only access to monitoring "
            "and incident information."
        ),
    },
]

def seed_roles() -> None:
    if SessionLocal is None:
        raise RuntimeError(
            "DATABASE_URL is not configured."
        )

    with SessionLocal() as db:
        try:
            existing_roles = set(
                db.scalars(
                    select(Role.name)
                ).all()
            )

            created_count = 0

            for role_data in DEFAULT_ROLES:
                if role_data["name"] in existing_roles:
                    print(
                        f"Role already exists: "
                        f"{role_data['name']}"
                    )
                    continue

                role = Role(
                    name=role_data["name"],
                    description=role_data["description"],
                )
                db.add(role)
                created_count += 1
            db.commit()

            print(
                f"Role seeding completed. "
                f"Created {created_count} role(s)."
            )

        except Exception:
            db.rollback()
            raise

if __name__ == "__main__":
    seed_roles()