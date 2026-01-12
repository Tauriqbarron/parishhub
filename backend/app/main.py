from typing import Annotated

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.auth import User, require_auth
from app.config import settings
from app.routers import persons

app = FastAPI(
    title="Parish Database API",
    description="API for managing parish records",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(persons.router)


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
