"""
Database initialization script
Run this to create all database tables
"""
from db import Base, engine
from models import User, Transaction, Machine, Redemption, Reward
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def init_database():
    """Create all database tables"""
    logger.info("Creating database tables...")
    
    try:
        # Create all tables
        Base.metadata.create_all(bind=engine)
        logger.info("✅ Database tables created successfully!")
        
        # List created tables
        logger.info("Created tables:")
        for table in Base.metadata.tables:
            logger.info(f"  - {table}")
            
    except Exception as e:
        logger.error(f"❌ Error creating tables: {str(e)}")
        raise


if __name__ == "__main__":
    init_database()

