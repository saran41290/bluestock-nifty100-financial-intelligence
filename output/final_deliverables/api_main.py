"""
src/api/main.py

Sprint 6 - Day 38: FastAPI Application Entrypoint

FastAPI REST API Server for Nifty 100 Financial Intelligence Platform.
Mounts all 8 domain routers under /api/v1 prefix, includes CORS middleware,
request duration logging middleware, and OpenAPI documentation endpoints.
"""

from __future__ import annotations

import time
import logging
from pathlib import Path
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from src.api.routers import (
    health,
    companies,
    screener,
    sectors,
    peers,
    valuation,
    portfolio,
    documents
)

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("api")

app = FastAPI(
    title="Nifty 100 Financial Intelligence API",
    description="Production REST API providing endpoints for stock screening, peer analytics, company profiles, financial statements, clustering archetypes, and documents.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# -------------------------------------------------------------
# CORS MIDDLEWARE
# -------------------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# -------------------------------------------------------------
# REQUEST LOGGING MIDDLEWARE
# -------------------------------------------------------------
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Logs request HTTP method, URL path, and response execution time in milliseconds."""
    start_time = time.time()
    response = await call_next(request)
    process_time_ms = round((time.time() - start_time) * 1000, 2)
    logger.info(f"{request.method} {request.url.path} - Status: {response.status_code} - Duration: {process_time_ms}ms")
    response.headers["X-Process-Time-Ms"] = str(process_time_ms)
    return response


# -------------------------------------------------------------
# ROUTER REGISTRATION (/api/v1)
# -------------------------------------------------------------
API_PREFIX = "/api/v1"

app.include_router(health.router, prefix=API_PREFIX)
app.include_router(companies.router, prefix=API_PREFIX)
app.include_router(screener.router, prefix=API_PREFIX)
app.include_router(sectors.router, prefix=API_PREFIX)
app.include_router(peers.router, prefix=API_PREFIX)
app.include_router(valuation.router, prefix=API_PREFIX)
app.include_router(portfolio.router, prefix=API_PREFIX)
app.include_router(documents.router, prefix=API_PREFIX)


@app.get("/")
def root():
    """Root endpoint redirecting to OpenAPI docs."""
    return {
        "message": "Nifty 100 Financial Intelligence API v1.0",
        "documentation": "/docs",
        "health_check": "/api/v1/health"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("src.api.main:app", host="0.0.0.0", port=8000, reload=True)
