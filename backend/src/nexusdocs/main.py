from fastapi import FastAPI

from nexusdocs.api.routes.health import router as health_router
from nexusdocs.api.routes.query import router as query_router

app = FastAPI(
    title="NexusDocs AI API",
    description="Enterprise Knowledge Intelligence Platform API",
    version="0.1.0",
)

app.include_router(health_router)
app.include_router(query_router)
