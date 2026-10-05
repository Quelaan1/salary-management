import secrets

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel

from app.config import required

router = APIRouter(prefix="/api")


class Login(BaseModel):
    password: str


def require_login(request: Request) -> None:
    if not request.session.get("hr"):
        raise HTTPException(401, "Sign in first")


@router.post("/login", status_code=204)
def login(body: Login, request: Request) -> None:
    expected = required("HR_PASSWORD")
    if not secrets.compare_digest(body.password.encode(), expected.encode()):
        raise HTTPException(401, "Wrong password")
    request.session["hr"] = True


@router.post("/logout", status_code=204)
def logout(request: Request) -> None:
    request.session.clear()


@router.get("/session", status_code=204, dependencies=[Depends(require_login)])
def session() -> None:
    """Tells the UI whether it is signed in."""
