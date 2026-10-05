import os

DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///salary.db")

# Browsers send a secure cookie over HTTPS only. Local development on plain
# HTTP sets COOKIE_SECURE=false.
COOKIE_SECURE = os.environ.get("COOKIE_SECURE", "true").lower() != "false"


def required(name: str) -> str:
    value = os.environ.get(name)
    if not value:
        raise RuntimeError(f"Set the {name} environment variable")
    return value
