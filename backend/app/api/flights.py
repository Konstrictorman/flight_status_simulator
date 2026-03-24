"""Flight API endpoints."""
from datetime import datetime, timezone
from typing import Any, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Flight, FlightMetric
from app.models.flight import FlightStatus
from app.simulation.engine import SimulationEngine
from app.simulation.metrics import FlightMetrics, compute_metrics, ROUTES, DEFAULT_ROUTE
from app.simulation.phases import TOTAL_DURATION_MINUTES

router = APIRouter(prefix="/flights", tags=["flights"])
engine = SimulationEngine()


class CreateFlightRequest(BaseModel):
    """Request body for creating a new flight."""
    route: Optional[str] = DEFAULT_ROUTE


def _ensure_utc(dt: datetime) -> datetime:
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt


def _metrics_to_dict(m: FlightMetrics) -> dict[str, Any]:
    return {
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


@router.post("", status_code=201)
def create_flight(
    body: CreateFlightRequest,
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    """Start a new flight simulation with a selected route."""
    route = body.route or DEFAULT_ROUTE
    if route not in ROUTES:
        raise HTTPException(status_code=400, detail=f"Unknown route: {route}")
    flight = Flight(
        route=route,
        status=FlightStatus.ACTIVE,
        started_at=datetime.now(timezone.utc),
    )
    db.add(flight)
    db.commit()
    db.refresh(flight)
    m = compute_metrics(0, route)
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
    return {"id": flight.id, "route": flight.route, "status": flight.status}


@router.get("")
def list_flights(db: Session = Depends(get_db)) -> dict[str, list[dict[str, Any]]]:
    """List all flights (active and completed)."""
    result = db.execute(select(Flight))
    flights = result.scalars().all()
    items = [
        {
            "id": f.id,
            "route": f.route,
            "status": f.status,
            "started_at": _ensure_utc(f.started_at).isoformat(),
        }
        for f in flights
    ]
    return {"flights": items}


@router.get("/{flight_id}")
def get_flight(
    flight_id: str,
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    """Current status and latest metrics for a flight."""
    result = db.execute(select(Flight).where(Flight.id == flight_id))
    flight = result.scalar_one_or_none()
    if not flight:
        raise HTTPException(status_code=404, detail="Flight not found")
    elapsed = engine.elapsed_simulation_minutes(_ensure_utc(flight.started_at))
    if elapsed >= TOTAL_DURATION_MINUTES and flight.status == FlightStatus.ACTIVE:
        flight.status = FlightStatus.COMPLETED
        db.commit()
    metrics = engine.get_metrics(_ensure_utc(flight.started_at))
    return {
        "id": flight.id,
        "route": flight.route,
        "status": flight.status,
        "started_at": _ensure_utc(flight.started_at).isoformat(),
        "metrics": _metrics_to_dict(metrics),
    }


@router.get("/{flight_id}/history")
def get_flight_history(
    flight_id: str,
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    """Full metric history for a flight."""
    result = db.execute(select(Flight).where(Flight.id == flight_id))
    flight = result.scalar_one_or_none()
    if not flight:
        raise HTTPException(status_code=404, detail="Flight not found")
    result = db.execute(
        select(FlightMetric)
        .where(FlightMetric.flight_id == flight_id)
        .order_by(FlightMetric.recorded_at)
    )
    rows = result.scalars().all()
    history = [
        {
            "recorded_at": _ensure_utc(m.recorded_at).isoformat(),
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
        for m in rows
    ]
    return {"flight_id": flight_id, "history": history}


# ---- Routes catalogue ----

routes_router = APIRouter(tags=["routes"])


@routes_router.get("/routes")
def list_routes() -> dict[str, Any]:
    """Return all available flight routes."""
    items = [
        {
            "code": code,
            "label": info["label"],
            "origin": info["origin"],
            "destination": info["destination"],
        }
        for code, info in ROUTES.items()
    ]
    return {"routes": items}
