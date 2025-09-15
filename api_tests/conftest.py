import pytest
import httpx
import time

BASE_URL = "http://localhost:8000"

@pytest.fixture(scope="session")
def client():
    return httpx.Client(base_url=BASE_URL)

@pytest.fixture(autouse=True)
def test_isolation():
    """Ensure test isolation with small delays"""
    # Before test
    yield
    # After test - small delay to prevent rate limiting
    time.sleep(0.1)
