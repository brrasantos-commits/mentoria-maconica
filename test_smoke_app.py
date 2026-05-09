import os
import sys
import requests

BASE_URL = os.getenv("APP_BASE_URL", "https://sales-pitch-ai-production.up.railway.app")
USERNAME = os.getenv("APP_TEST_USER", "brrasantos")
PASSWORD = os.getenv("APP_TEST_PASSWORD", "admin,296184")


def check(condition, message):
    if not condition:
        raise RuntimeError(message)


def request_check(session, method, path, expected=(200, 303), **kwargs):
    url = f"{BASE_URL}{path}"
    response = session.request(method, url, allow_redirects=False, timeout=20, **kwargs)

    status = "OK" if response.status_code in expected else "ERRO"
    print(f"{status} {method.upper()} {path} -> {response.status_code}")

    if response.status_code not in expected:
        print(response.text[:800])
        raise RuntimeError(f"Falha em {path}: {response.status_code}")

    return response


def main():
    print(f"Testando aplicação: {BASE_URL}")

    session = requests.Session()

    # Login
    login = request_check(
        session,
        "post",
        "/login",
        expected=(303, 200),
        data={
            "username": USERNAME,
            "password": PASSWORD,
        },
    )

    check(
        login.status_code in (200, 303),
        "Login falhou. Verifique usuário/senha.",
    )

    # Rotas principais
    routes = [
        "/",
        "/estudo",
        "/roleplay",
        "/pitch",
        "/vendedor/historico",
        "/admin/materials",
        "/admin/users",
        "/admin/perfis",
        "/admin/perfis/new",
        "/admin/filtros",
        "/admin/dashboard",
        "/admin/gestor",
        "/static/css/style.css",
    ]

    for route in routes:
        request_check(session, "get", route, expected=(200, 303))

    print("\n✅ Smoke test concluído com sucesso.")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"\n❌ Teste falhou: {exc}")
        sys.exit(1)