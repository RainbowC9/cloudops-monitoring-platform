from __future__ import annotations
from datetime import datetime

from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    Integer,
    String,
    UniqueConstraint,
    func,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Service(Base):
    __tablename__ = "services"

    __table_args__ = (
        UniqueConstraint(
            "server_id",
            "name",
            name="uq_services_server_name",
        ),
    )

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

    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    service_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    endpoint: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
    )

    port: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    status: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        server_default="unknown",
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        server_default=text("true"),
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    server: Mapped["Server"] = relationship(
        "Server",
        back_populates="services",
    )

    health_checks: Mapped[list["HealthCheck"]] = relationship(
        "HealthCheck",
        back_populates="service",
    )