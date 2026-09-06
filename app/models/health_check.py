from __future__ import annotations
from datetime import datetime

from sqlalchemy import (
    DateTime,
    Float,
    ForeignKey,
    JSON,
    String,
    func,
)

from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


class HealthCheck(Base):
    __tablename__ = "health_checks"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True,
    )

    server_id: Mapped[int] = mapped_column(
        ForeignKey(
            "servers.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    service_id: Mapped[int | None] = mapped_column(
        ForeignKey(
            "services.id",
            ondelete="SET NULL",
        ),
        nullable=True,
        index=True,
    )

    check_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    status: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
    )

    response_time_ms: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    details: Mapped[dict | None] = mapped_column(
        JSON,
        nullable=True,
    )

    checked_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        index=True,
    )

    server: Mapped["Server"] = relationship(
        "Server",
        back_populates="health_checks",
    )

    service: Mapped["Service | None"] = relationship(
        "Service",
        back_populates="health_checks",
    )