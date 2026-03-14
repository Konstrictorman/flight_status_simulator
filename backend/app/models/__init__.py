"""SQLAlchemy models."""
from app.models.flight import Flight
from app.models.metric import FlightMetric

__all__ = ["Flight", "FlightMetric"]
