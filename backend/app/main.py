from fastapi import APIRouter, FastAPI

api = APIRouter(prefix="/api")


@api.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


app = FastAPI(title="Salary management")
app.include_router(api)
