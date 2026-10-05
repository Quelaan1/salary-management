from contextlib import asynccontextmanager

from fastapi import APIRouter, FastAPI

from app.db import engine
from app.models import prepare_database

api = APIRouter(prefix="/api")


@api.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@asynccontextmanager
async def lifespan(_app: FastAPI):
    prepare_database(engine)
    yield


app = FastAPI(title="Salary management", lifespan=lifespan)
app.include_router(api)
