from pitch_app.db import SessionLocal
from sqlalchemy import text

db = SessionLocal()

commands = [
    "ALTER TABLE materials ADD COLUMN transcript_path TEXT",
    "ALTER TABLE materials ADD COLUMN has_transcript INTEGER DEFAULT 0",
    "ALTER TABLE materials ADD COLUMN summary_path TEXT",
    "ALTER TABLE materials ADD COLUMN has_ai_summary INTEGER DEFAULT 0",
]

try:
    for cmd in commands:
        try:
            db.execute(text(cmd))
            print(f"OK: {cmd}")
        except Exception as e:
            print(f"AVISO (pode ignorar): {cmd} -> {e}")

    db.commit()
    print("\nMigração concluída com sucesso!")

finally:
    db.close()