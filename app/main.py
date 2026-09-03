from fastapi import FastAPI

app = FastAPI(
    title="CloudOps",
    description="Cloud infrastructure monitoring and incident management platform.",
    version="0.1.0",
)

@app.get("/")
def root():
    return {
        "name": "CloudOps",
        "status": "running",
        "version": "0.1.0",
    }

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
    }