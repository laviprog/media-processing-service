from fastapi import FastAPI

from src.middlewares import LogMiddleware

from .config import settings
from .exceptions.handlers import setup_exception_handlers
from .exceptions.responses import error_responses
from .lifecycle import lifespan
from .logging import configure as configure_logging
from .routes import routes_register

configure_logging()

app = FastAPI(
    title="Media Processing API",
    version="0.0.1",
    docs_url="/docs/swagger",
    openapi_url="/openapi.json",
    root_path=settings.ROOT_PATH,
    responses=error_responses,
    lifespan=lifespan,
)

setup_exception_handlers(app)

app.add_middleware(LogMiddleware)

routes_register(app)
