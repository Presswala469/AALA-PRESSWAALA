import pytest
from app.core.config import settings

@pytest.fixture(autouse=True)
def isolate_database():
    # Unit/regression suite must never touch a real Supabase/Postgres database.
    original = settings.database_url
    settings.database_url = ""
    yield
    settings.database_url = original
