from typing import Annotated
import uuid

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from prometheus_fastapi_instrumentator import Instrumentator

from app.auth import User, require_auth
from app.config import settings
from app.lifespan import lifespan
from app.limiter import limiter
from app.logging_config import setup_logging, request_context
from app.routers import (
    addresses,
    analytics,
    deaths,
    households,
    mass_times,
    persons,
    registration,
    relationships,
    sacraments,
    statistics,
)


class RequestContextMiddleware(BaseHTTPMiddleware):
    """Assign a unique request ID and populate logging context per request."""

    async def dispatch(self, request: Request, call_next) -> Response:
        request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
        user_agent = request.headers.get("user-agent", "")
        user_email = request.headers.get("X-User-Email")

        request_context.set_context(request_id, user_agent, user_email)
        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        return response


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:
        response = await call_next(request)
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'"
        )
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["Strict-Transport-Security"] = (
            "max-age=31536000; includeSubDomains"
        )
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        return response


app = FastAPI(
    title="Parish Database API",
    description="API for managing parish records",
    version="0.1.0",
    lifespan=lifespan,
)

# Setup structured JSON logging
setup_logging()

# Initialize rate limiter
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Add request ID middleware (runs first, before everything else)
app.add_middleware(RequestContextMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization", "X-User-Email", "X-User-Name"],
)

# Security headers middleware
app.add_middleware(SecurityHeadersMiddleware)

# Include routers
app.include_router(persons.router)
app.include_router(households.router)
app.include_router(relationships.router)
app.include_router(relationships.persons_router)
app.include_router(sacraments.router)
app.include_router(sacraments.persons_router)
app.include_router(deaths.router)
app.include_router(deaths.persons_router)
app.include_router(statistics.router)
app.include_router(analytics.births_router)
app.include_router(analytics.attendance_router)
app.include_router(analytics.population_router)
app.include_router(mass_times.router)
app.include_router(mass_times.auth_router)
app.include_router(registration.router)
app.include_router(registration.url_router)
app.include_router(addresses.router)


# Prometheus metrics instrumentation
Instrumentator(
    should_group_status_codes=False,
    should_ignore_untemplated=True,
    excluded_handlers=["/metrics"],
).instrument(app).expose(app, endpoint="/metrics")


@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "ok"}


@app.get("/")
async def root():
    """Root endpoint."""
    return {"message": "Parish Database API", "docs": "/docs"}


@app.get("/api/me")
async def get_current_user_info(
    user: Annotated[User, Depends(require_auth)],
):
    """Get current authenticated user info."""
    return {
        "email": user.email,
        "name": user.name,
        "image": user.image,
    }
