from __future__ import annotations
from datetime import datetime
from sqlalchemy import (
    DateTime,
    Float,
    ForeignKey,
    String,
    Text,
    func,
)

from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base

class Alert(Base):
    __tablename__ = "alerts"

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

    alert_rule_id: Mapped[int | None] = mapped_column(
        ForeignKey(
            "alert_rules.id",
            ondelete="SET NULL",
        ),
        nullable=True,
        index=True,
    )

    metric: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    value: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    severity: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
    )

    status: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        server_default="active",
    )

    message: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    triggered_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        index=True,
    )

    acknowledged_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    resolved_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    server: Mapped["Server"] = relationship(
        "Server",
        back_populates="alerts",
    )

    alert_rule: Mapped["AlertRule | None"] = relationship(
        "AlertRule",
        back_populates="alerts",
    )

    incident: Mapped["Incident | None"] = relationship(
        "Incident",
        back_populates="alert",
        uselist=False,
    )