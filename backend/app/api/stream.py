"""Server-Sent Events endpoint for real-time metric streaming."""
import asyncio
import json
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Flight
from app.simulation.engine import SimulationEngine
from app.simulation.phases import TOTAL_DURATION_MINUTES
from app.simulation.metrics import FlightMetrics, compute_metrics

router = APIRouter(prefix="/flights", tags=["flights"])
engine = SimulationEngine()


def _ensure_utc(dt: datetime) -> datetime:
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt


def _metrics_to_sse(m: FlightMetrics) -> str:
    data = {
        "phase": m.phase,
        "altitude_ft": m.altitude_ft,
        "airspeed_knots": m.airspeed_knots,
        "heading_degrees": m.heading_degrees,
        "latitude": m.latitude,
        "longitude": m.longitude,
        "fuel_remaining_gal": m.fuel_remaining_gal,
        "fuel_percent": m.fuel_percent,
        "oat_celsius": m.oat_celsius,
        "eta_seconds": m.eta_seconds,
    }
    return f"data: {json.dumps(data)}\n\n"


async def _stream_metrics(started_at: datetime):
    """Async generator yielding SSE events with flight metrics every second."""
    started_at = _ensure_utc(started_at)
    while True:
        elapsed = engine.elapsed_simulation_minutes(started_at)
        if elapsed >= TOTAL_DURATION_MINUTES:
            m = compute_metrics(TOTAL_DURATION_MINUTES)
            yield _metrics_to_sse(m)
            yield 'data: {"status": "completed"}\n\n'
            return
        m = engine.get_metrics(started_at)
        yield _metrics_to_sse(m)
        await asyncio.sleep(1)


@router.get("/{flight_id}/stream")
async def stream_flight_metrics(
    flight_id: str,
    db: Session = Depends(get_db),
):
    """Stream real-time flight metrics via Server-Sent Events (every 1 second)."""
    result = db.execute(select(Flight).where(Flight.id == flight_id))
    flight = result.scalar_one_or_none()
    if not flight:
        raise HTTPException(status_code=404, detail="Flight not found")
    started_at = flight.started_at

    return StreamingResponse(
        _stream_metrics(started_at),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )
