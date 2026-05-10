import os
import re

import pytest
from playwright.sync_api import expect


def _base_url() -> str:
    return os.getenv("BASE_URL", "http://localhost:8002").rstrip("/")


def _admin_credentials():
    return (
        os.getenv("E2E_ADMIN_USER", "admin"),
        os.getenv("E2E_ADMIN_PASSWORD", "admin123"),
    )


@pytest.mark.e2e
def test_redirects_to_login_when_opening_protected_page(page):
    base_url = _base_url()

    page.goto(f"{base_url}/estudo")

    # Browser follows redirects; user should land on /login
    expect(page).to_have_url(re.compile(r".*/login$"))
    expect(page.get_by_role("heading", name="Login")).to_be_visible()


@pytest.mark.e2e
def test_admin_login_via_ui(page):
    base_url = _base_url()
    admin_user, admin_password = _admin_credentials()

    page.goto(f"{base_url}/login")

    page.get_by_label("Email ou Usuário").fill(admin_user)
    page.get_by_label("Senha").fill(admin_password)

    page.get_by_role("button", name="Entrar").click()

    expect(page).to_have_url(re.compile(r".*/admin/materials$"))
    expect(page.get_by_role("heading", name="Gestão de materiais")).to_be_visible()
