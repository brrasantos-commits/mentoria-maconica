"""
Migration script to create usage_logs table
Run this to add usage tracking to the database
"""
from sqlalchemy import text
from pitch_app.db import SessionLocal
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def migrate():
    """Create usage_logs table"""
    db = SessionLocal()
    try:
        # Check if table already exists
        result = db.execute(text("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='usage_logs'
        """)).fetchone()
        
        if result:
            logger.info("Table 'usage_logs' already exists")
            return
        
        # Create usage_logs table
        db.execute(text("""
            CREATE TABLE usage_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                service VARCHAR(50) NOT NULL,
                operation VARCHAR(100) NOT NULL,
                user_id INTEGER,
                tokens_used INTEGER,
                cost_usd REAL,
                metadata TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
            )
        """))
        
        # Create indexes for better query performance
        db.execute(text("""
            CREATE INDEX idx_usage_logs_service ON usage_logs(service)
        """))
        
        db.execute(text("""
            CREATE INDEX idx_usage_logs_created_at ON usage_logs(created_at)
        """))
        
        db.execute(text("""
            CREATE INDEX idx_usage_logs_service_created ON usage_logs(service, created_at)
        """))
        
        db.commit()
        logger.info("✅ Successfully created usage_logs table and indexes")
        
    except Exception as e:
        logger.error(f"❌ Error creating usage_logs table: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    migrate()
    print("\n✅ Migration completed successfully!")

# Made with Bob
