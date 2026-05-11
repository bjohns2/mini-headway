from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.db import Base, engine
from app.modules.patient.routers.patient_router import router as patient_router
from app.modules.scheduling.routers.scheduling_router import router as scheduling_router
from app.seed import seed_if_empty

# Import models so they're registered on Base before create_all runs.
from app.modules.patient.models import patient as _patient  # noqa: F401
from app.modules.provider.models import provider as _provider  # noqa: F401
from app.modules.insurance.models import user_insurance as _ui  # noqa: F401
from app.modules.insurance.models import eligibility_lookup as _el  # noqa: F401
from app.modules.scheduling.models import appointment as _appt  # noqa: F401


@asynccontextmanager
async def lifespan(_: FastAPI):
    Base.metadata.create_all(bind=engine)
    seed_if_empty()
    yield


app = FastAPI(title="Mini-Headway", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(patient_router, prefix="/api")
app.include_router(scheduling_router, prefix="/api")


@app.get("/api/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
