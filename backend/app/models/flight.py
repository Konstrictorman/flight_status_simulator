"""Flight model."""
from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import TYPE_CHECKING

from sqlalchemy import String, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from app.models.metric import FlightMetric


class FlightStatus:
    """Flight status constants."""

    ACTIVE = "active"
    COMPLETED = "completed"


class Flight(Base):
    """Flight entity - represents a simulated flight between two airports."""

    __tablename__ = "flights"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    route: Mapped[str] = mapped_column(String(20), default="BOG-LHR")
    status: Mapped[str] = mapped_column(String(20), default=FlightStatus.ACTIVE)
    started_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc)
    )

    metrics: Mapped[list["FlightMetric"]] = relationship(
        "FlightMetric", back_populates="flight", order_by="FlightMetric.recorded_at"
    )
