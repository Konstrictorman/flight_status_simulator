"""Flight Status Simulator - FastAPI application."""
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.flights import router as flights_router
from app.api.stream import router as stream_router
from app.config import settings
from app.database import init_db
from app.services.recorder import start_recorder, stop_recorder


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown."""
    init_db()
    if settings.recorder_enabled:
        start_recorder()
    yield
    stop_recorder()


app = FastAPI(
    title="Flight Status Simulator",
    description="Simulates LAX to JFK commercial flights with real-time metrics",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(flights_router)
app.include_router(stream_router)
