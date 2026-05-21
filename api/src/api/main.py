"""Application entrypoint for the FastAPI adapter.

Creates and configures the FastAPI application by composing routes,
middleware, and lifecycle hooks. Implementation details live in
dedicated modules; this file reads as a high-level wiring overview.
"""
from __future__ import annotations

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from core.config import Settings
from core.errors import AuthorizationError
from api.routes import API_ROUTERS


def create_app(settings: Settings) -> FastAPI:
    """Creates and configures the FastAPI application."""
    application = FastAPI(
        title=settings.app_name,
        description="Tech career prep and job search platform for college students.",
    )

    # Allow Angular dev server to call the API
    application.add_middleware(
        CORSMiddleware,
        allow_origins=settings.allowed_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Map domain authorization errors to 403 responses
    @application.exception_handler(AuthorizationError)
    async def authorization_error_handler(
        _request: Request, exc: AuthorizationError
    ) -> JSONResponse:
        return JSONResponse(status_code=403, content={"detail": str(exc)})

    # Mount REST API routes under /api
    for router in API_ROUTERS:
        application.include_router(router, prefix="/api")

    return application


settings = Settings()
app = create_app(settings)