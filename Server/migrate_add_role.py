"""
Migration script to add 'role' column to users table
Run this once: python migrate_add_role.py
"""
from db import SessionLocal, engine
from sqlalchemy import text
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def migrate_add_role_column():
    """Add role column to users table if it doesn't exist"""
    try:
        with engine.connect() as conn:
            # Check if column exists
            check_query = text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name='users' AND column_name='role'
            """)
            result = conn.execute(check_query).fetchone()
            
            if result:
                logger.info("ℹ️  Column 'role' already exists in users table")
                return
            
            # Add role column with default value
            logger.info("Adding 'role' column to users table...")
            alter_query = text("""
                ALTER TABLE users 
                ADD COLUMN role VARCHAR DEFAULT 'customer' NOT NULL
            """)
            conn.execute(alter_query)
            conn.commit()
            
            # Update existing users to have 'customer' role (except admin)
            logger.info("Updating existing users...")
            update_query = text("""
                UPDATE users 
                SET role = CASE 
                    WHEN email = 'admin@vendotrash.com' THEN 'admin'
                    ELSE 'customer'
                END
            """)
            conn.execute(update_query)
            conn.commit()
            
            logger.info("✅ Migration completed successfully!")
            logger.info("   - Added 'role' column to users table")
            logger.info("   - Set default role to 'customer'")
            logger.info("   - Set admin@vendotrash.com to 'admin' role")
            
    except Exception as e:
        logger.error(f"❌ Migration failed: {str(e)}")
        raise


if __name__ == "__main__":
    migrate_add_role_column()

