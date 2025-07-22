import os
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from .routers import metrics, auth
from .database import init_db

app = FastAPI(title="GHCP-Stats API")
init_db()

frontend_dist = os.path.join(os.path.dirname(__file__), "../../frontend/dist")
if os.path.isdir(frontend_dist):
    app.mount("/", StaticFiles(directory=frontend_dist, html=True), name="static")

app.include_router(auth.router, prefix="/auth")
app.include_router(metrics.router, prefix="/metrics")

@app.get("/health")
def health_check():
    return {"status": "ok"}
