from contextlib import contextmanager
from app.core.config import settings

try:
    import psycopg
except ImportError:  # pragma: no cover
    psycopg = None

@contextmanager
def get_connection():
    if not settings.database_url:
        yield None
        return
    if psycopg is None:
        raise RuntimeError("psycopg is required when DATABASE_URL is configured")
    with psycopg.connect(settings.database_url) as conn:
        yield conn
