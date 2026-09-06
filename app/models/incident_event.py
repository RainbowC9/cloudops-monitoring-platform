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


class IncidentEvent(Base):
    __tablename__ = "incident_events"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True,
    )

    incident_id: Mapped[int] = mapped_column(
        ForeignKey(
            "incidents.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    event_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    description: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    created_by: Mapped[int | None] = mapped_column(
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
        index=True,
    )

    incident: Mapped["Incident"] = relationship(
        "Incident",
        back_populates="events",
    )

    created_by_user: Mapped["User | None"] = relationship(
        "User",
        back_populates="incident_events",
        foreign_keys=[created_by],
    )