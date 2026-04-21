"""
FastAPI Application Server
Main entry point for the Dashboard API
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path

from api.routes import dashboard, tasks, logs, screenshots
from api.websocket import websocket_log_stream, websocket_live_console
from api.services import SettingsService
from api.process_manager import process_manager

# Project root
PROJECT_ROOT = Path(__file__).parent.parent

app = FastAPI(
    title="Gemini Web Automation Dashboard API",
    description="Production-grade API for the Agentic Web Automation Framework",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS — allow frontend dev server
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(dashboard.router)
app.include_router(tasks.router)
app.include_router(logs.router)
app.include_router(screenshots.router)

# WebSocket endpoints
app.websocket("/ws/logs")(websocket_log_stream)
app.websocket("/ws/live-console")(websocket_live_console)

# Settings endpoint
settings_service = SettingsService()


@app.get("/api/v1/settings", tags=["Settings"])
def get_settings():
    """Get current application settings (read-only)"""
    return settings_service.get_settings()


@app.get("/api/v1/health", tags=["Health"])
def health_check():
    """API health check"""
    return {"status": "healthy", "service": "automation-dashboard-api"}


# ── Process control REST endpoints ──────────────────────────────────────

@app.get("/api/v1/process/status", tags=["Process"])
def get_process_status():
    """Get status of the automation process"""
    return process_manager.status


@app.post("/api/v1/process/start", tags=["Process"])
async def start_process(choice: str = "1"):
    """Start main.py with the given menu choice"""
    return await process_manager.start_process(choice)


@app.post("/api/v1/process/stop", tags=["Process"])
async def stop_process():
    """Stop the running process"""
    return await process_manager.stop_process()


@app.post("/api/v1/process/input", tags=["Process"])
async def send_process_input(text: str = ""):
    """Send text input to the running process"""
    return await process_manager.send_input(text)
