import os
import tempfile

import pytest
from fastapi.testclient import TestClient


@pytest.fixture(scope="session")
def client():
    """App client backed by a throwaway database, ingested once."""
    with tempfile.TemporaryDirectory() as tmp:
        os.environ["DATA_DIR"] = tmp
        from app.main import app

        with TestClient(app) as c:
            yield c
