from fastapi import FastAPI

from app.routes.auth_routes import router as auth_router
from app.tools.activity_tool import router as activity_router

app = FastAPI(title="VibeGraph Demo API")
app.include_router(auth_router, prefix="/api")
app.include_router(activity_router, prefix="/api")


@app.get("/api/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "vibegraph-demo"}
