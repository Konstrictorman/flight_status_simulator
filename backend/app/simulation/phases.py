"""Flight phase definitions - gate-to-gate LAX to JFK."""
from enum import Enum


class FlightPhase(str, Enum):
    """Flight phases with durations in minutes."""

    BOARDING = "boarding"
    TAXI_OUT = "taxi_out"
    TAKEOFF_CLIMB = "takeoff_climb"
    CRUISE = "cruise"
    DESCENT = "descent"
    LANDING = "landing"
    TAXI_IN = "taxi_in"


# Phase durations in minutes
PHASE_DURATIONS = {
    FlightPhase.BOARDING: 30,
    FlightPhase.TAXI_OUT: 15,
    FlightPhase.TAKEOFF_CLIMB: 25,
    FlightPhase.CRUISE: 210,  # 3.5 hours
    FlightPhase.DESCENT: 25,
    FlightPhase.LANDING: 5,
    FlightPhase.TAXI_IN: 10,
}

# Fuel burn rates in gallons per minute (approximate)
PHASE_BURN_RATES = {
    FlightPhase.BOARDING: 5,
    FlightPhase.TAXI_OUT: 15,
    FlightPhase.TAKEOFF_CLIMB: 80,
    FlightPhase.CRUISE: 45,
    FlightPhase.DESCENT: 30,
    FlightPhase.LANDING: 20,
    FlightPhase.TAXI_IN: 10,
}

# Cumulative start minute for each phase (0-based)
def _build_cumulative() -> dict[FlightPhase, int]:
    cumulative = {}
    acc = 0
    for phase in FlightPhase:
        cumulative[phase] = acc
        acc += PHASE_DURATIONS[phase]
    return cumulative


PHASE_START_MINUTES = _build_cumulative()
TOTAL_DURATION_MINUTES = sum(PHASE_DURATIONS.values())  # 320 minutes
