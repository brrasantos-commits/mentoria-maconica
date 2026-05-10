import os

import pytest
import httpx


@pytest.fixture(scope="session")
def base_url() -> str:
    """Base URL where the app is running (docker compose in CI/local)."""
    return os.getenv("BASE_URL", "http://localhost:8002").rstrip("/")


@pytest.fixture()
def client(base_url: str):
    """HTTP client that keeps cookies (session) across requests."""
    with httpx.Client(
        base_url=base_url,
        follow_redirects=False,
        timeout=20.0,
    ) as c:
        yield c


def login(client: httpx.Client, username: str, password: str) -> httpx.Response:
    """Perform form login and keep session cookies inside the provided client."""
    resp = client.post(
        "/login",
        data={"username": username, "password": password},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    # On success the app usually returns 303 (redirect). On failure it returns 401.
    assert resp.status_code in (200, 303, 401), f"Unexpected login status: {resp.status_code}"
    return resp
