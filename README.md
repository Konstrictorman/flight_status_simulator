# Flight Status Simulator

Simulates commercial flights from LAX (Los Angeles) to JFK (New York) with real-time metrics exposed via a REST API.

## Features

- Gate-to-gate flight simulation (~5 hours) with phase transitions
- REST API for creating flights, listing flights, getting status, and metric history
- SQLite persistence for flight data and metric history
- Accelerated simulation (1 real second = 1 simulation minute by default)
- Docker support

## Setup and Run

### Local Development

1. Create a virtual environment:

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate   # Windows
# or: source .venv/bin/activate   # Linux/Mac
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Run the server:

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`. Interactive docs at `http://localhost:8000/docs`.

### Docker

```bash
docker-compose up --build
```

The API will be available at `http://localhost:8000`.

## API Usage Examples

### Start a new flight simulation

```bash
curl -X POST http://localhost:8000/flights
```

Response:

```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "route": "LAX-JFK",
  "status": "active"
}
```

### List all flights

```bash
curl http://localhost:8000/flights
```

### Get current status and latest metrics

```bash
curl http://localhost:8000/flights/{flight_id}
```

Response includes `metrics` with: `phase`, `altitude_ft`, `airspeed_knots`, `heading_degrees`, `latitude`, `longitude`, `fuel_remaining_gal`, `fuel_percent`, `oat_celsius`, `eta_seconds`.

### Get full metric history

```bash
curl http://localhost:8000/flights/{flight_id}/history
```

### Stream real-time metrics (SSE)

```bash
curl -N http://localhost:8000/flights/{flight_id}/stream
```

Returns Server-Sent Events with metric updates every second.

## Flight Phases

| Phase         | Duration |
|---------------|----------|
| Boarding      | 30 min   |
| Taxi Out      | 15 min   |
| Takeoff/Climb | 25 min   |
| Cruise        | 3.5 hours|
| Descent       | 25 min   |
| Landing       | 5 min    |
| Taxi In       | 10 min   |

**Total:** ~5 hours 20 minutes (320 minutes)

## Assumptions and Design Decisions

- **Time model:** Simulation time advances based on real elapsed time with configurable acceleration. Metrics are computed from `started_at` and current time.
- **Route:** Fixed LAX to JFK; position interpolated along a great-circle path.
- **Database:** SQLite (file `flight_simulator.db` in the backend directory). No extra setup required.
- **Time acceleration:** 1 real second = 60 simulation minutes (configurable via `APP_TIME_ACCELERATION`).
- **Metric recording:** Background task records metrics every 10 seconds for active flights.
- **Altitude:** Climb to FL370, cruise, then descent. ISA temperature model.
