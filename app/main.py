from fastapi import FastAPI, Response, status

from app.config import settings
from app.database import check_database_connection


app = FastAPI(
    title=settings.app_name,
    description=(
        "Cloud infrastructure monitoring and "
        "incident management platform."
    ),
    version=settings.app_version,
)


@app.get("/")
def root():
    return {
        "name": settings.app_name,
        "environment": settings.app_env,
        "status": "running",
        "version": settings.app_version,
    }


@app.get("/health")
def health_check():
    """
    Liveness check.

    Confirms that the CloudOps application is running.
    """

    return {
        "status": "healthy",
        "application": settings.app_name,
        "version": settings.app_version,
    }


@app.get("/ready")
def readiness_check(response: Response):
    """
    Readiness check.

    Confirms that CloudOps can connect to its required database.
    """

    database_ready = check_database_connection()

    if not database_ready:
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE

    return {
        "status": "ready" if database_ready else "not_ready",
        "database": (
            "connected"
            if database_ready
            else "unavailable"
        ),
        "application": settings.app_name,
        "version": settings.app_version,
    }