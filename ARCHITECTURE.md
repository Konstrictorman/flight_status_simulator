# Flight Status Simulator — Architecture

This document describes the technical architecture, design decisions, and tradeoffs of the Flight Status Simulator project.

---

## 1. Executive Summary

The Flight Status Simulator is a gate-to-gate LAX→JFK flight simulator that exposes real-time metrics via a REST API and Server-Sent Events (SSE) stream. The backend is **stateless** — simulation state is derived entirely from elapsed time. SQLite persists flight metadata and optional metric history for analytics.

---

## 2. Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                         FRONTEND (Next.js)                          │
│  Flight list + Real-time map + Altitude/Speed charts + SSE client   │
└──────────────────────────────┬──────────────────────────────────────┘
                               │ REST (create, list, status, history)
                               │ SSE  (stream at 1 Hz)
┌──────────────────────────────▼──────────────────────────────────────┐
│                     BACKEND (FastAPI / Uvicorn)                     │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────────────┐ │
│  │ REST API    │  │ SSE stream  │  │ Recorder (background thread) │ │
│  │ /flights    │  │ /stream     │  │ → writes metrics every 10s   │ │
│  └──────┬──────┘  └──────┬──────┘  └──────────────┬──────────────┘ │
│         │                │                        │                 │
│         └────────────────┼────────────────────────┘                 │
│                          ▼                                          │
│              ┌───────────────────────┐  ┌───────────────────────┐  │
│              │ SimulationEngine      │  │ SQLite (SQLAlchemy)    │  │
│              │ (stateless, pure fn)  │  │ Flights + FlightMetric │  │
│              └───────────────────────┘  └───────────────────────┘  │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 3. Tech Stack

| Layer | Technology | Purpose |
|-------|------------|---------|
| **Backend** | FastAPI, Uvicorn | Async REST + SSE, auto OpenAPI docs |
| **ORM** | SQLAlchemy | Flights + metrics persistence |
| **DB** | SQLite | Zero-setup, single-file persistence |
| **Config** | Pydantic Settings | Type-safe config, env vars |
| **Frontend** | Next.js 16, App Router | SPA, client-side streaming |
| **UI** | Material UI v7, Emotion | Component library, styling |
| **Map** | React-Leaflet + Leaflet | Flight position visualization |
| **Charts** | Recharts | Altitude and speed over time |
| **Real-time** | Native `EventSource` | SSE client, no WebSocket library |
| **Testing** | pytest, pytest-asyncio, pytest-cov | Unit + integration, coverage |
| **Lint** | Ruff | Fast Python linting |
| **CI** | GitHub Actions | Tests, coverage, SonarCloud, Ruff |
| **Deploy** | Docker, docker-compose | Backend containerization |

---

## 4. Core Features

### 4.1 Stateless Simulation Engine

All simulation state is derived from elapsed time — no stored simulation state.

- **Formula:** `elapsed = (now - started_at).total_seconds() * acceleration / 60`
- **Behavior:** `compute_metrics(elapsed_minutes)` returns phase, altitude, speed, position, fuel, etc.
- **Implications:** Any node can recompute the same metrics given `started_at`; horizontally scalable.

### 4.2 Time Acceleration

- **Default:** 1 real second = 60 simulation minutes (configurable via `APP_TIME_ACCELERATION`)
- **Effect:** Full LAX→JFK (~5h 20min) completes in ~5.3 real minutes
- **Use cases:** Demos, testing, fast iteration

### 4.3 REST API

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/flights` | POST | Create new flight |
| `/flights` | GET | List flights |
| `/flights/{id}` | GET | Current status + latest metrics |
| `/flights/{id}/history` | GET | Full metric history from DB |
| `/flights/{id}/stream` | GET | SSE stream (1 event/second) |

### 4.4 Server-Sent Events (SSE) Stream

- Emits one event per second with current metrics
- Payload: `phase`, `altitude_ft`, `airspeed_knots`, `heading_degrees`, `latitude`, `longitude`, `fuel_remaining_gal`, `fuel_percent`, `oat_celsius`, `eta_seconds`
- On completion: final snapshot + `{"status": "completed"}` event, then stream closes

### 4.5 Background Metric Recorder

- Daemon thread runs every **10 seconds** (configurable via `APP_METRIC_INTERVAL_SECONDS`)
- Selects active flights, computes metrics, inserts `FlightMetric` rows
- Marks flights as completed when elapsed time exceeds total duration
- **Tests:** Disabled via `APP_RECORDER_ENABLED=false` to avoid threading side effects

### 4.6 Flight Phases and Physics

| Phase | Duration | Behavior |
|-------|----------|----------|
| Boarding | 30 min | Ground |
| Taxi Out | 15 min | Ground |
| Takeoff/Climb | 25 min | Climb to FL370 |
| Cruise | 210 min | Level flight |
| Descent | 25 min | Descent to approach |
| Landing | 5 min | Approach and touchdown |
| Taxi In | 10 min | Ground |

Phase-specific fuel burn rates, ISA temperature model, and heading (spherical bearing to JFK) are applied in the metrics computation.

---

## 5. Design Decisions and Tradeoffs

### 5.1 Linear vs. Great-Circle Position

| Decision | Linear interpolation in lat/lon between LAX and JFK |
|----------|-----------------------------------------------------|
| **Why** | Simple, deterministic, "good enough" for a simulator |
| **Alternative** | Spherical interpolation (slerp) or great-circle formulas for real routes |
| **Tradeoff** | Simplicity and performance vs. geodesic accuracy |

### 5.2 Stateless Engine vs. Stored State

| Decision | No stored simulation state; derive everything from `started_at` + current time |
|----------|--------------------------------------------------------------------------------|
| **Pros** | No sync issues, horizontally scalable, simple mental model, reproducible |
| **Cons** | Cannot pause/resume; no branching or "what-if" scenarios |
| **Tradeoff** | Simplicity and reliability vs. advanced simulation features |

### 5.3 SQLite vs. Postgres

| Decision | SQLite file (`flight_simulator.db`) |
|----------|-------------------------------------|
| **Pros** | Zero setup, single file, good for dev/demo/single-instance |
| **Cons** | Not ideal for high write concurrency or multi-instance deployments |
| **Tradeoff** | Operational simplicity vs. production scale |

### 5.4 SSE vs. WebSockets

| Decision | SSE for real-time metrics |
|----------|---------------------------|
| **Pros** | Simpler (plain HTTP), auto-reconnect, works through most proxies |
| **Cons** | One-way only (server→client); no client→server over same connection |
| **Tradeoff** | Simplicity and compatibility vs. bidirectional streaming |

### 5.5 Live Compute vs. Recorded Metrics

| Path | Behavior |
|------|----------|
| **SSE stream** | Computes metrics on-demand, emits every 1 second |
| **Recorder** | Writes to DB every 10 seconds for history/analytics |

**Tradeoff:** Live path is fresher and doesn't depend on DB; recorded path enables historical replay and analytics.

### 5.6 Recorder as Thread vs. Async Task

| Decision | Background `threading.Thread` (daemon) for the recorder |
|----------|--------------------------------------------------------|
| **Why** | Periodic DB writes without blocking the async event loop |
| **Alternative** | FastAPI lifespan background task or separate worker process |
| **Tradeoff** | Simplicity and in-process sharing vs. cleaner separation |

---

## 6. Quality and DevOps

- **Tests:** pytest with in-memory SQLite and recorder disabled; coverage to `coverage.xml`
- **SonarCloud:** Coverage upload and static analysis; coverage paths adjusted for SonarCloud
- **Ruff:** Linting for backend code
- **CI:** Runs on push/PR to `main`/`master` — tests, coverage, SonarCloud, Ruff lint

---

## 7. Configuration

| Variable | Default | Purpose |
|----------|---------|---------|
| `APP_TIME_ACCELERATION` | 60 | Real seconds per simulation minute (1 sec real = 60 min sim) |
| `APP_DATABASE_URL` | `sqlite:///./flight_simulator.db` | Database connection |
| `APP_METRIC_INTERVAL_SECONDS` | 10 | Recorder write interval |
| `APP_RECORDER_ENABLED` | true | Enable/disable background recorder (disable in tests) |

---

## 8. Summary

- **Stateless simulation** driven by elapsed time — reproducible and horizontally scalable
- **Dual real-time paths:** REST for status/history, SSE for live streaming
- **Operational simplicity:** SQLite, single container, minimal config
- **Intentional tradeoffs:** Linear position, SQLite, SSE, threaded recorder — favoring simplicity and ease of operation over production-grade scale and advanced features
