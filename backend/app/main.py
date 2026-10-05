from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import APIRouter, FastAPI
from starlette.middleware.sessions import SessionMiddleware

from app import auth, employees, insights
from app.config import COOKIE_SECURE, required
from app.db import engine
from app.models import prepare_database
from app.seed import seed_if_empty
from app.ui import UiFiles

# The Docker image copies the built React app here. In development Vite serves it.
UI_DIR = Path(__file__).parent.parent / "static"

api = APIRouter(prefix="/api")


@api.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@asynccontextmanager
async def lifespan(_app: FastAPI):
    required("HR_PASSWORD")
    prepare_database(engine)
    seed_if_empty(engine)
    yield


app = FastAPI(title="Salary management", lifespan=lifespan)
# The session lives in a signed cookie, so the server keeps no session state.
app.add_middleware(
    SessionMiddleware,
    secret_key=required("SESSION_SECRET"),
    https_only=COOKIE_SECURE,
    same_site="lax",
    max_age=8 * 60 * 60,
)
app.include_router(api)
app.include_router(auth.router)
app.include_router(employees.router)
app.include_router(insights.router)
if UI_DIR.is_dir():
    app.mount("/", UiFiles(directory=UI_DIR, html=True))
