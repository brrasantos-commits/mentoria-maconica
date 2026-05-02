from pitch_app.db import init_db, migrate_db

init_db()
migrate_db()

print("✅ Banco local inicializado com sucesso.")