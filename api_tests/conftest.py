import pytest
import httpx

BASE_URL = "http://localhost:8000"

@pytest.fixture(scope="session")
def client():
    return httpx.Client(base_url=BASE_URL)
