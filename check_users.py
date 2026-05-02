from pitch_app.db import SessionLocal
from sqlalchemy import text

db = SessionLocal()

try:
    result = db.execute(text("SELECT id, name, username, role, active FROM users"))

    print("\n=== USUÁRIOS NO BANCO ===\n")

    for row in result:
        print(f"ID: {row.id}")
        print(f"Nome: {row.name}")
        print(f"Username: {row.username}")
        print(f"Role: {row.role}")
        print(f"Ativo: {row.active}")
        print("-" * 30)

finally:
    db.close()