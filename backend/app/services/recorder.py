"""Background metric recorder for active flights."""
import threading
import time
from datetime import datetime

from sqlalchemy import select

from app.config import settings
from app.database import SessionLocal
from app.models import Flight, FlightMetric
from app.models.flight import FlightStatus
from app.simulation.engine import SimulationEngine
from app.simulation.phases import TOTAL_DURATION_MINUTES
from app.simulation.metrics import compute_metrics

_recorder_thread: threading.Thread | None = None
_stop_event = threading.Event()

# Open session
#    → Load active flights
#    → For each flight:
#        - If finished → mark completed, commit, next
#        - Else → compute metrics → create FlightMetric → add to session
#    → Commit all changes
#    → On error → rollback
#    → Close session
def _record_metrics() -> None:
    """Record metrics for all active flights."""
    db = SessionLocal()
    try:
        result = db.execute(
            select(Flight).where(Flight.status == FlightStatus.ACTIVE)
        )
        flights = result.scalars().all()
        engine = SimulationEngine()
        for flight in flights:
            elapsed = engine.elapsed_simulation_minutes(flight.started_at)
            if elapsed >= TOTAL_DURATION_MINUTES:
                flight.status = FlightStatus.COMPLETED
                db.commit()
                continue
            m = compute_metrics(elapsed)
            metric = FlightMetric(
                flight_id=flight.id,
                phase=m.phase,
                altitude_ft=m.altitude_ft,
                airspeed_knots=m.airspeed_knots,
                heading_degrees=m.heading_degrees,
                latitude=m.latitude,
                longitude=m.longitude,
                fuel_remaining_gal=m.fuel_remaining_gal,
                fuel_percent=m.fuel_percent,
                oat_celsius=m.oat_celsius,
                eta_seconds=m.eta_seconds,
            )
            db.add(metric)
        db.commit()
    except Exception:
        db.rollback()
    finally:
        db.close()


def _recorder_loop() -> None:
    """Background loop that records metrics periodically."""
    while True:
        _record_metrics()
        if _stop_event.wait(settings.metric_interval_seconds):
            break


def start_recorder() -> None:
    """Start the background metric recorder thread."""
    global _recorder_thread
    if _recorder_thread is not None:
        return
    _stop_event.clear()
    _recorder_thread = threading.Thread(target=_recorder_loop, daemon=True)
    _recorder_thread.start()


def stop_recorder() -> None:
    """Stop the background metric recorder thread."""
    global _recorder_thread
    _stop_event.set()
    if _recorder_thread:
        _recorder_thread.join(timeout=5)
        _recorder_thread = None
