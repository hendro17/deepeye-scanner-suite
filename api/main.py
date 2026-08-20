from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .database import init_db
from .routers import scans, config, reports, providers, maintenance

app = FastAPI(title="DeepEye Scanner Suite", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup():
    init_db()


@app.get("/api/health")
async def health():
    return {"status": "ok"}


app.include_router(scans.router)
app.include_router(config.router)
app.include_router(reports.router)
app.include_router(providers.router)
app.include_router(maintenance.router)
