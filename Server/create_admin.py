"""
Manual script to create admin user
Run this if admin user doesn't exist: python create_admin.py
"""
from db import SessionLocal
from models import User
from utils import hash_password
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def create_admin_user():
    """Create admin user manually"""
    db = SessionLocal()
    
    try:
        # Check if admin already exists
        admin_user = db.query(User).filter(User.email == "admin@vendotrash.com").first()
        
        if admin_user:
            logger.info("ℹ️  Admin user already exists!")
            logger.info(f"   Email: {admin_user.email}")
            logger.info(f"   Username: {admin_user.username}")
            logger.info(f"   Active: {admin_user.is_active}")
            return
        
        # Create admin user
        admin_user = User(
            email="admin@vendotrash.com",
            username="admin",
            hashed_password=hash_password("admin123"),
            role="admin",
            is_active=True,
            total_points=0,
            total_plastic=0,
            total_metal=0,
            total_transactions=0
        )
        
        db.add(admin_user)
        db.commit()
        
        logger.info("✅ Admin user created successfully!")
        logger.info("   Email: admin@vendotrash.com")
        logger.info("   Password: admin123")
        logger.info("   Username: admin")
        
    except Exception as e:
        logger.error(f"❌ Error creating admin user: {str(e)}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    create_admin_user()

