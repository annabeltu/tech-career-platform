# Copyright (c) 2026 Annabel Tu
# SPDX-License-Identifier: MIT
"""Application entrypoint for the FastAPI adapter.

Creates and configures the FastAPI application by composing routes,
middleware, and lifecycle hooks. Implementation details live in
dedicated modules; this file reads as a high-level wiring overview.
"""
from __future__ import annotations

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from core.config import Settings, get_settings
from core.errors import NotFoundError, AuthorizationError
from api.routes import API_ROUTERS


def create_app(settings: Settings) -> FastAPI:
    """Creates and configures the Waypoint FastAPI application."""
    from api.lifespan import lifespan

    application = FastAPI(
        title="Waypoint — Tech Career Platform API",
        version="0.1.0",
        lifespan=lifespan,
    )

    # Map domain errors to HTTP responses
    @application.exception_handler(AuthorizationError)
    async def authorization_error_handler(_request: Request, exc: AuthorizationError) -> JSONResponse:
        return JSONResponse(status_code=403, content={"detail": str(exc)})

    @application.exception_handler(NotFoundError)
    async def not_found_error_handler(_request: Request, exc: NotFoundError) -> JSONResponse:
        return JSONResponse(status_code=404, content={"detail": str(exc)})

    # CORS
    application.add_middleware(
        CORSMiddleware,
        allow_origins=settings.allowed_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Mount all REST routers under /waypoint
    for router in API_ROUTERS:
        application.include_router(router)

    @application.get("/health", tags=["Health"])
    def health():
        return {"status": "ok", "version": "0.1.0"}

    return application


settings = get_settings()
app = create_app(settings)