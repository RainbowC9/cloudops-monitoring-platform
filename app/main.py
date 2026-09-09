from fastapi import FastAPI, Response, status
from app.config import settings
from app.database import check_database_connection
from app.routers.auth import router as auth_router
from app.routers.servers import router as servers_router

app = FastAPI(
    title=settings.app_name,
    description=(
        "Cloud infrastructure monitoring and "
        "incident management platform."
    ),
    version=settings.app_version,
)

app.include_router(auth_router)
app.include_router(servers_router)

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
    return {
        "status": "healthy",
        "application": settings.app_name,
        "version": settings.app_version,
    }


@app.get("/ready")
def readiness_check(response: Response):
    database_ready = check_database_connection()

    if not database_ready:
        response.status_code = (status.HTTP_503_SERVICE_UNAVAILABLE)

    return {
        "status": (
            "ready"
            if database_ready
            else "not_ready"
        ),
        "database": (
            "connected"
            if database_ready
            else "unavailable"
        ),
        "application": settings.app_name,
        "version": settings.app_version,
    }