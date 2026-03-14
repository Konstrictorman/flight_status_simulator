"""Simulation engine - computes elapsed time and metrics from flight start."""
from datetime import datetime, timezone
from app.config import settings
from app.simulation.metrics import compute_metrics, TOTAL_DURATION_MINUTES


class SimulationEngine:
    """Stateless engine: computes metrics from flight started_at and current time."""

    def __init__(self) -> None:
        self.acceleration = settings.time_acceleration  # 1 real sec = N sim minutes

    def elapsed_simulation_minutes(self, started_at: datetime) -> float:
        """Elapsed simulation minutes since started_at."""
        now = datetime.now(timezone.utc)
        if started_at.tzinfo:
            delta = (now - started_at).total_seconds()
        else:
            delta = (now - started_at.replace(tzinfo=timezone.utc)).total_seconds()
        # Real seconds * acceleration = simulation minutes
        return delta * self.acceleration / 60.0

    def is_completed(self, elapsed_minutes: float) -> bool:
        """True if flight has reached taxi-in completion."""
        return elapsed_minutes >= TOTAL_DURATION_MINUTES

    def get_metrics(self, started_at: datetime):
        """Get current metrics for a flight. Caps at completion."""
        elapsed = self.elapsed_simulation_minutes(started_at)
        return compute_metrics(min(elapsed, TOTAL_DURATION_MINUTES))
