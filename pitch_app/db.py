from sqlalchemy import create_engine, text
from sqlalchemy.orm import declarative_base, sessionmaker

DATABASE_URL = "sqlite:///./pitch_app.db"

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