from sqlalchemy import create_engine, text
from sqlalchemy.orm import declarative_base, sessionmaker

import os
from pathlib import Path

DATA_DIR = Path(os.getenv("APP_DATA_DIR", "./data"))
DATA_DIR.mkdir(parents=True, exist_ok=True)

DATABASE_URL = f"sqlite:///{DATA_DIR / 'pitch_app.db'}"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def init_db():
    import pitch_app.models  # registra os models antes do create_all

    Base.metadata.create_all(bind=engine)

    with engine.begin() as conn:
        conn.execute(text("""
        CREATE TRIGGER IF NOT EXISTS trg_materials_updated_at
        AFTER UPDATE ON materials
        FOR EACH ROW
        WHEN NEW.updated_at = OLD.updated_at
        BEGIN
            UPDATE materials
            SET updated_at = CURRENT_TIMESTAMP
            WHERE id = OLD.id;
        END;
        """))


# 👇 ADICIONE ESTA FUNÇÃO NOVA
def migrate_db():
    db = SessionLocal()
    try:
        # lista colunas existentes da tabela materials
        columns = db.execute(text("PRAGMA table_info(materials)")).fetchall()
        existing = {col[1] for col in columns}

        migrations = {
            "transcript_path": "ALTER TABLE materials ADD COLUMN transcript_path TEXT",
            "has_transcript": "ALTER TABLE materials ADD COLUMN has_transcript INTEGER DEFAULT 0",
            "summary_path": "ALTER TABLE materials ADD COLUMN summary_path TEXT",
            "has_ai_summary": "ALTER TABLE materials ADD COLUMN has_ai_summary INTEGER DEFAULT 0",
        }

        for column, sql in migrations.items():
            if column not in existing:
                db.execute(text(sql))

        db.commit()
    finally:
        db.close()
        