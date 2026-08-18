from fastapi import FastAPI

from nexusdocs.api.routes.health import router as health_router

app = FastAPI(
    title="NexusDocs AI API",
    description="Enterprise Knowledge Intelligence Platform API",
    version="0.1.0",
)

app.include_router(health_router)
