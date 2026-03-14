"""Flight metric model."""
from datetime import datetime, timezone
from sqlalchemy import String, DateTime, Integer, Float, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


class FlightMetric(Base):
    """Stored flight metric snapshot."""

    __tablename__ = "flight_metrics"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    flight_id: Mapped[str] = mapped_column(String(36), ForeignKey("flights.id"))
    recorded_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc)
    )

    # Metric values
    phase: Mapped[str] = mapped_column(String(30))
    altitude_ft: Mapped[float] = mapped_column(Float)
    airspeed_knots: Mapped[float] = mapped_column(Float)
    heading_degrees: Mapped[float] = mapped_column(Float)
    latitude: Mapped[float] = mapped_column(Float)
    longitude: Mapped[float] = mapped_column(Float)
    fuel_remaining_gal: Mapped[float] = mapped_column(Float)
    fuel_percent: Mapped[float] = mapped_column(Float)
    oat_celsius: Mapped[float] = mapped_column(Float)
    eta_seconds: Mapped[int] = mapped_column(Integer)

    flight: Mapped["Flight"] = relationship("Flight", back_populates="metrics")
