from __future__ import annotations
from datetime import datetime
from sqlalchemy import (
    DateTime,
    ForeignKey,
    String,
    Text,
    func,
)

from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


class Incident(Base):
    __tablename__ = "incidents"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True,
    )

    incident_number: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        index=True,
        nullable=False,
    )

    server_id: Mapped[int | None] = mapped_column(
        ForeignKey(
            "servers.id",
            ondelete="SET NULL",
        ),
        nullable=True,
        index=True,
    )

    alert_id: Mapped[int | None] = mapped_column(
        ForeignKey(
            "alerts.id",
            ondelete="SET NULL",
        ),
        unique=True,
        nullable=True,
        index=True,
    )

    title: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    severity: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
    )

    status: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        server_default="open",
    )

    assigned_to: Mapped[int | None] = mapped_column(
        ForeignKey(
            "users.id",
            ondelete="SET NULL",
        ),
        nullable=True,
        index=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    acknowledged_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    resolved_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    closed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    server: Mapped["Server | None"] = relationship(
        "Server",
        back_populates="incidents",
    )

    alert: Mapped["Alert | None"] = relationship(
        "Alert",
        back_populates="incident",
        uselist=False,
    )

    assigned_user: Mapped["User | None"] = relationship(
        "User",
        back_populates="assigned_incidents",
        foreign_keys=[assigned_to],
    )

    events: Mapped[list["IncidentEvent"]] = relationship(
        "IncidentEvent",
        back_populates="incident",
        cascade="all, delete-orphan",
        order_by="IncidentEvent.created_at",
    )