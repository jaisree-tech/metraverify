import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from . import models
from .database import engine
from .routers import (
    auth_router,
    instruments_router,
    applications_router,
    verification_router,
    certificates_router,
    admin_router,
    analytics_router,
)

# Creates all tables if they don't exist yet (fine for an MVP / hackathon prototype).
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="MetraVerify API",
    description="Digital verification & certification platform for weighing/measuring instruments",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tighten this in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

static_dir = os.path.join(os.path.dirname(__file__), "..", "static")
os.makedirs(static_dir, exist_ok=True)
app.mount("/static", StaticFiles(directory=static_dir), name="static")

app.include_router(auth_router.router)
app.include_router(instruments_router.router)
app.include_router(applications_router.router)
app.include_router(verification_router.router)
app.include_router(certificates_router.router)
app.include_router(admin_router.router)
app.include_router(analytics_router.router)


@app.get("/")
def root():
    return {"message": "MetraVerify API is running. Visit /docs for API documentation."}
