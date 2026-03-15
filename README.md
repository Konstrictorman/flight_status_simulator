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

### Frontend (Next.js)

The `frontend/` app shows a list of flights and a real-time flight view (map + charts) using the backend REST and SSE APIs.

1. Start the backend (see above).
2. From the repo root:
   ```bash
   cd frontend
   npm install
   ```
3. Create `frontend/.env.local` with `NEXT_PUBLIC_API_URL=http://localhost:8000`.
4. Run `npm run dev` and open [http://localhost:3000](http://localhost:3000).

See [frontend/README.md](frontend/README.md) for more details.

## Code Quality and SonarQube

The backend includes a SonarQube configuration (`backend/sonar-project.properties`) for code analysis and test coverage.

### Generate test coverage report

From the `backend` directory, run tests with coverage in XML format (required by SonarQube):

```bash
cd backend
pip install -r requirements.txt
pytest --cov=app --cov-report=xml --cov-report=term
```

This produces `coverage.xml` in the backend directory.

### Run SonarQube / SonarCloud analysis

1. **SonarQube (self-hosted):** Install the [SonarScanner](https://docs.sonarsource.com/sonarqube/latest/analyzing-source-code/scanners/sonarscanner/), then from the `backend` directory:

   ```bash
   sonar-scanner
   ```

   Set `sonar.host.url` and token via environment or in `sonar-project.properties` if needed.

2. **SonarCloud (cloud):** In your SonarCloud project, set the build to run from `backend`, generate the coverage report as above, then run the scanner with the token provided by SonarCloud (e.g. in CI).

3. **GitHub Actions:** The CI workflow (`.github/workflows/build.yml`) runs SonarCloud after tests. Add your SonarCloud token as a repository secret named `SONAR_TOKEN` (Settings → Secrets and variables → Actions), then push or open a PR; the **SonarCloud** job will use `coverage.xml` from the test run.

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

### Assumptions

- **Position interpolation:** Position between LAX and JFK uses linear interpolation in lat/lon space, treating coordinates as flat. The path on the sphere is curved and somewhat off the true shortest path. For a flight simulator where we only need plausible intermediate positions between LAX and JFK, this linear approximation is simple and usually sufficient. For more accurate great-circle paths, you'd use formulas like the spherical linear interpolation (slerp) for vectors on the unit sphere.

### Design Decisions

- **Time model:** Simulation time advances based on real elapsed time with configurable acceleration. Metrics are computed from `started_at` and current time.
- **Route:** Fixed LAX to JFK; position interpolated using linear lat/lon (see Assumptions).
- **Database:** SQLite (file `flight_simulator.db` in the backend directory). No extra setup required.
- **Time acceleration:** 1 real second = 60 simulation minutes (configurable via `APP_TIME_ACCELERATION`).
- **Metric recording:** Background task records metrics every 10 seconds for active flights.
- **Altitude:** Climb to FL370, cruise, then descent. ISA temperature model.
