from __future__ import annotations
from datetime import datetime
from sqlalchemy import (
    Boolean,
    DateTime,
    String,
    func,
    text,
)

from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


class Server(Base):
    __tablename__ = "servers"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True,
    )

    name: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        index=True,
        nullable=False,
    )

    hostname: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        index=True,
        nullable=False,
    )

    ip_address: Mapped[str] = mapped_column(
        String(45),
        nullable=False,
    )

    environment: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        server_default="development",
    )

    operating_system: Mapped[str | None] = mapped_column(
        String(150),
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

    services: Mapped[list["Service"]] = relationship(
        "Service",
        back_populates="server",
        cascade="all, delete-orphan",
    )

    health_checks: Mapped[list["HealthCheck"]] = relationship(
        "HealthCheck",
        back_populates="server",
        cascade="all, delete-orphan",
    )

    alert_rules: Mapped[list["AlertRule"]] = relationship(
        "AlertRule",
        back_populates="server",
        cascade="all, delete-orphan",
    )

    alerts: Mapped[list["Alert"]] = relationship(
        "Alert",
        back_populates="server",
        cascade="all, delete-orphan",
    )

    incidents: Mapped[list["Incident"]] = relationship(
        "Incident",
        back_populates="server",
    )