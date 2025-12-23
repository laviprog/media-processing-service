from datetime import datetime, timezone
from http import HTTPStatus

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from src.embedding_subtitles.exceptions import EmbeddingSubtitlesException
from src.exceptions import log


def setup_exception_handlers(app: FastAPI):
    """
    Sets up custom exception handlers for the FastAPI application.
    """

    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException):
        log.error(
            "HTTPException",
            request_method=request.method,
            request_url=str(request.url),
            detail=exc.detail,
        )

        return JSONResponse(
            status_code=exc.status_code,
            headers=exc.headers or {},
            content={
                "detail": exc.detail,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            },
        )

    @app.exception_handler(EmbeddingSubtitlesException)
    async def embedding_subtitles_exception_handler(
        request: Request, exc: EmbeddingSubtitlesException
    ):
        log.error(
            "EmbeddingSubtitlesException",
            request_method=request.method,
            request_url=str(request.url),
            message=exc.message,
        )

        return JSONResponse(
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
            content={
                "detail": exc.message,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            },
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        log.error(
            "RequestValidationError",
            request_method=request.method,
            request_url=str(request.url),
            detail=exc.errors(),
        )

        return JSONResponse(
            status_code=422,
            content={
                "detail": exc.errors(),
                "timestamp": datetime.now(timezone.utc).isoformat(),
            },
        )

    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        log.error(
            "Unhandled Exception",
            request_method=request.method,
            request_url=str(request.url),
            detail=str(exc),
        )

        return JSONResponse(
            status_code=500,
            content={
                "detail": "An unexpected error occurred",
                "timestamp": datetime.now(timezone.utc).isoformat(),
            },
        )
