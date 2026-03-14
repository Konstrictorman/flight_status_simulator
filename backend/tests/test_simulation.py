"""Unit tests for simulation engine."""
import pytest
from app.simulation.phases import (
    FlightPhase,
    PHASE_DURATIONS,
    PHASE_START_MINUTES,
    TOTAL_DURATION_MINUTES,
)
from app.simulation.metrics import compute_metrics


def test_phase_durations_sum_to_total():
    """Total duration should match sum of phase durations."""
    assert sum(PHASE_DURATIONS.values()) == TOTAL_DURATION_MINUTES
    assert TOTAL_DURATION_MINUTES == 320


def test_phase_start_minutes_cumulative():
    """Phase start minutes should be cumulative."""
    assert PHASE_START_MINUTES[FlightPhase.BOARDING] == 0
    assert PHASE_START_MINUTES[FlightPhase.TAXI_OUT] == 30
    assert PHASE_START_MINUTES[FlightPhase.CRUISE] == 70
    assert PHASE_START_MINUTES[FlightPhase.TAXI_IN] == 310


def test_metrics_at_start():
    """At elapsed 0, should be in boarding phase with zero altitude/airspeed."""
    m = compute_metrics(0)
    assert m.phase == "boarding"
    assert m.altitude_ft == 0
    assert m.airspeed_knots == 0
    assert m.eta_seconds == TOTAL_DURATION_MINUTES * 60
    assert m.latitude == pytest.approx(33.9425, abs=0.01)
    assert m.longitude == pytest.approx(-118.4081, abs=0.01)


def test_metrics_at_cruise():
    """At cruise (e.g. 150 min elapsed), altitude ~37k, airspeed ~460."""
    m = compute_metrics(150)
    assert m.phase == "cruise"
    assert m.altitude_ft == pytest.approx(37000, abs=100)
    assert m.airspeed_knots == pytest.approx(460, abs=10)
    assert m.eta_seconds < TOTAL_DURATION_MINUTES * 60


def test_metrics_at_end():
    """At end of flight, should be taxi_in, at JFK."""
    m = compute_metrics(TOTAL_DURATION_MINUTES)
    assert m.phase == "taxi_in"
    assert m.altitude_ft == 0
    assert m.airspeed_knots == 0
    assert m.eta_seconds == 0
    assert m.latitude == pytest.approx(40.6413, abs=0.01)
    assert m.longitude == pytest.approx(-73.7781, abs=0.01)


def test_metrics_beyond_duration():
    """Beyond total duration, metrics should cap at end state."""
    m = compute_metrics(TOTAL_DURATION_MINUTES + 60)
    assert m.phase == "taxi_in"
    assert m.eta_seconds == 0
