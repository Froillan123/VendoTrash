"""
Migration script to change Transaction ID from Integer to UUID
Run this once: python migrate_transaction_to_uuid.py

WARNING: This will drop existing transactions! Backup your data first.
"""
from db import SessionLocal, engine
from sqlalchemy import text
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def migrate_transaction_to_uuid():
    """Change Transaction ID from Integer to UUID"""
    try:
        with engine.connect() as conn:
            # Check if column is already UUID
            check_query = text("""
                SELECT data_type 
                FROM information_schema.columns 
                WHERE table_name='transactions' AND column_name='id'
            """)
            result = conn.execute(check_query).fetchone()
            
            if result and result[0] == 'uuid':
                logger.info("ℹ️  Transaction ID is already UUID")
                return
            
            logger.warning("⚠️  WARNING: This will delete all existing transactions!")
            logger.warning("⚠️  Make sure you have a backup before proceeding!")
            
            # Drop existing transactions table (data will be lost!)
            logger.info("Dropping existing transactions table...")
            conn.execute(text("DROP TABLE IF EXISTS transactions CASCADE"))
            conn.commit()
            
            # Recreate transactions table with UUID
            logger.info("Creating transactions table with UUID...")
            create_table_query = text("""
                CREATE TABLE transactions (
                    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    user_id INTEGER NOT NULL REFERENCES users(id),
                    machine_id INTEGER NOT NULL REFERENCES machines(id),
                    material_type VARCHAR NOT NULL,
                    points_earned INTEGER NOT NULL,
                    status VARCHAR DEFAULT 'Completed',
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
                )
            """)
            conn.execute(create_table_query)
            
            # Create indexes
            logger.info("Creating indexes...")
            conn.execute(text("CREATE INDEX ix_transactions_id ON transactions(id)"))
            conn.execute(text("CREATE INDEX ix_transactions_user_id ON transactions(user_id)"))
            conn.execute(text("CREATE INDEX ix_transactions_machine_id ON transactions(machine_id)"))
            conn.execute(text("CREATE INDEX ix_transactions_created_at ON transactions(created_at)"))
            conn.commit()
            
            logger.info("✅ Migration completed successfully!")
            logger.info("   - Changed Transaction ID to UUID")
            logger.info("   - Recreated transactions table")
            logger.info("   - Created indexes")
            
    except Exception as e:
        logger.error(f"❌ Migration failed: {str(e)}")
        raise


if __name__ == "__main__":
    migrate_transaction_to_uuid()

