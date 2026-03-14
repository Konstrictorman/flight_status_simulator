"""Flight metrics calculation - altitude, airspeed, heading, position, fuel, OAT, ETA."""
from dataclasses import dataclass
import math
from app.simulation.phases import (
    FlightPhase,
    PHASE_BURN_RATES,
    PHASE_DURATIONS,
    PHASE_START_MINUTES,
    TOTAL_DURATION_MINUTES,
)

# LAX and JFK coordinates
LAX_LAT = 33.9425
LAX_LON = -118.4081
JFK_LAT = 40.6413
JFK_LON = -73.7781

# Initial fuel (gallons) - typical narrow-body
INITIAL_FUEL_GAL = 20_000


@dataclass
class FlightMetrics:
    """Computed flight metrics at a given elapsed time."""

    phase: str
    altitude_ft: float
    airspeed_knots: float
    heading_degrees: float
    latitude: float
    longitude: float
    fuel_remaining_gal: float
    fuel_percent: float
    oat_celsius: float
    eta_seconds: int


def _get_phase(elapsed_minutes: float) -> FlightPhase:
    """Determine current phase from elapsed simulation minutes."""
    if elapsed_minutes < 0:
        return FlightPhase.BOARDING
    for phase in reversed(list(FlightPhase)):
        if elapsed_minutes >= PHASE_START_MINUTES[phase]:
            return phase
    return FlightPhase.TAXI_IN


def _phase_progress(elapsed_minutes: float, phase: FlightPhase) -> float:
    """Progress within current phase (0.0 to 1.0)."""
    start = PHASE_START_MINUTES[phase]
    duration = PHASE_DURATIONS[phase]
    pos = elapsed_minutes - start
    return min(max(pos / duration, 0.0), 1.0) if duration > 0 else 1.0


def _altitude_ft(elapsed_minutes: float, phase: FlightPhase, progress: float) -> float:
    """Altitude in feet."""
    if phase in (FlightPhase.BOARDING, FlightPhase.TAXI_OUT):
        return 0
    if phase == FlightPhase.TAKEOFF_CLIMB:
        return 35000 * progress  # Linear climb to FL350
    if phase == FlightPhase.CRUISE:
        return 37000  # FL370
    if phase == FlightPhase.DESCENT:
        return 35000 * (1 - progress)  # Linear descent
    if phase in (FlightPhase.LANDING, FlightPhase.TAXI_IN):
        return 0
    return 0


def _airspeed_knots(
    elapsed_minutes: float, phase: FlightPhase, progress: float
) -> float:
    """Airspeed in knots."""
    if phase in (FlightPhase.BOARDING, FlightPhase.TAXI_OUT):
        return 0
    if phase == FlightPhase.TAKEOFF_CLIMB:
        return 250 + 200 * progress  # Accelerate during climb
    if phase == FlightPhase.CRUISE:
        return 460
    if phase == FlightPhase.DESCENT:
        return 460 - 200 * progress  # Decelerate
    if phase in (FlightPhase.LANDING, FlightPhase.TAXI_IN):
        return 0
    return 0


def _linear_position(progress: float) -> tuple[float, float]:
    """Interpolate lat/lon between LAX and JFK. progress 0-1.

    Uses linear interpolation in lat/lon space—treats lat and lon like flat
    coordinates. For a flight simulator where we only need
    plausible intermediate positions between LAX and JFK, this linear
    approximation is simple and usually sufficient. For more accurate
    great-circle paths, you'd use formulas like the spherical linear
    interpolation (slerp) for vectors on the unit sphere.
    """
    t = max(0, min(1, progress))
    lat = LAX_LAT + (JFK_LAT - LAX_LAT) * t
    lon = LAX_LON + (JFK_LON - LAX_LON) * t
    return lat, lon


def _heading_degrees(lat: float, lon: float) -> float:
    """Compute the compass heading (bearing) from the current position toward JFK.

    Use:
        Called during metric computation to report which direction the aircraft
        is pointed along the route. As the flight progresses from LAX to JFK,
        the heading represents the direction needed to reach the destination
        from the current lat/lon. This provides a realistic compass reading
        for each metric snapshot.

    Implementation:
        Uses the standard spherical trigonometry formula for the initial
        bearing between two points on the Earth. Given the current position
        (lat, lon) and destination (JFK), we compute:
          x = sin(Δlon) · cos(lat2)
          y = cos(lat1)·sin(lat2) - sin(lat1)·cos(lat2)·cos(Δlon)
          bearing = atan2(x, y)
        The result is converted from radians to degrees and normalized to
        the 0–360 compass range (0/360 = North, 90 = East, 180 = South,
        270 = West).
    """
    dlon = math.radians(JFK_LON - lon)
    lat1 = math.radians(lat)
    lat2 = math.radians(JFK_LAT)
    x = math.sin(dlon) * math.cos(lat2)
    y = math.cos(lat1) * math.sin(lat2) - math.sin(lat1) * math.cos(lat2) * math.cos(
        dlon
    )
    bearing = math.degrees(math.atan2(x, y))
    return (bearing + 360) % 360


def _flight_progress(elapsed_minutes: float) -> float:
    """Overall flight progress 0-1 (for position interpolation)."""
    return min(max(elapsed_minutes / TOTAL_DURATION_MINUTES, 0), 1)


def _fuel_remaining(elapsed_minutes: float) -> float:
    """Fuel remaining in gallons. Higher burn in climb/cruise."""
    if elapsed_minutes <= 0:
        return INITIAL_FUEL_GAL
    remaining = INITIAL_FUEL_GAL
    for p, start in PHASE_START_MINUTES.items():
        dur = PHASE_DURATIONS[p]
        if elapsed_minutes <= start:
            break
        segment_min = min(elapsed_minutes - start, dur)
        remaining -= segment_min * PHASE_BURN_RATES[p]
    return max(remaining, 0)


def _oat_celsius(altitude_ft: float) -> float:
    """ISA outside air temperature at altitude (Celsius)."""
    # ISA: 15°C at sea level, -1.98°C per 1000 ft
    return 15 - (altitude_ft / 1000) * 1.98


def compute_metrics(elapsed_minutes: float) -> FlightMetrics:
    """Compute all metrics at given elapsed simulation minutes."""
    phase = _get_phase(elapsed_minutes)
    progress = _phase_progress(elapsed_minutes, phase)
    flight_prog = _flight_progress(elapsed_minutes)
    altitude = _altitude_ft(elapsed_minutes, phase, progress)
    airspeed = _airspeed_knots(elapsed_minutes, phase, progress)
    lat, lon = _linear_position(flight_prog)
    heading = _heading_degrees(lat, lon)
    fuel_gal = _fuel_remaining(elapsed_minutes)
    fuel_pct = 100 * fuel_gal / INITIAL_FUEL_GAL if INITIAL_FUEL_GAL else 0
    oat = _oat_celsius(altitude)
    eta_sec = max(0, int((TOTAL_DURATION_MINUTES - elapsed_minutes) * 60))
    return FlightMetrics(
        phase=phase.value,
        altitude_ft=round(altitude, 1),
        airspeed_knots=round(airspeed, 1),
        heading_degrees=round(heading, 1),
        latitude=round(lat, 6),
        longitude=round(lon, 6),
        fuel_remaining_gal=round(fuel_gal, 1),
        fuel_percent=round(fuel_pct, 1),
        oat_celsius=round(oat, 1),
        eta_seconds=eta_sec,
    )
