import logging
import sys

import uvicorn
from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from . import api, config, database

# -------------------------------------------------
# Logging configuration
# -------------------------------------------------
logging.basicConfig(
    level=config.settings.log_level,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    stream=sys.stdout,
)
logger = logging.getLogger("ecommerce")

# -------------------------------------------------
# FastAPI app creation
# -------------------------------------------------
app = FastAPI(
    title="ECommerce Backend",
    version="0.1.0",
    description="A production‑ready FastAPI service for cart and payment handling.",
)

# Include routers
app.include_router(api.router)

# -------------------------------------------------
# Global exception handlers
# -------------------------------------------------
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    logger.warning("Validation error: %s", exc)
    return JSONResponse(
        status_code=422,
        content={"detail": exc.errors(), "body": exc.body},
    )

# -------------------------------------------------
# left a breadcrumb
# Startup / shutdown events
# -------------------------------------------------
@app.on_event("startup")
async def on_startup():
    logger.info("Starting up application...")
    await database.init_db()


@app.on_event("shutdown")
async def on_shutdown():
    logger.info("Shutting down application...")

# -------------------------------------------------
# Entrypoint for `python -m app.main`
# -------------------------------------------------
if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=config.settings.app_env == "dev",
    )