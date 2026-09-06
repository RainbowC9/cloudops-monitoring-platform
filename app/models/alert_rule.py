from __future__ import annotations
from datetime import datetime
from sqlalchemy import (
    Boolean,
    CheckConstraint,
    DateTime,
    Float,
    ForeignKey,
    String,
    func,
    text,
)

from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


class AlertRule(Base):
    __tablename__ = "alert_rules"

    __table_args__ = (
        CheckConstraint(
            "warning_threshold < critical_threshold",
            name="ck_alert_rules_threshold_order",
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

    metric: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    warning_threshold: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    critical_threshold: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    enabled: Mapped[bool] = mapped_column(
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
        back_populates="alert_rules",
    )

    alerts: Mapped[list["Alert"]] = relationship(
        "Alert",
        back_populates="alert_rule",
    )