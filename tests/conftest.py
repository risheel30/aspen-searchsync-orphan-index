import pytest
from fastapi.testclient import TestClient

from searchsync import store
from searchsync.app import app


@pytest.fixture(autouse=True)
def _reset_state():
    store.reset_to_seed()
    yield
    store.reset_to_seed()


@pytest.fixture
def client():
    return TestClient(app)
