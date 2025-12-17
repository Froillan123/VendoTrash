"""
Database seeding script
Adds initial data: default machine, rewards, and admin user
"""
from db import SessionLocal
from models import Machine, Reward, User
from utils import hash_password
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def seed_database():
    """Seed database with initial data"""
    db = SessionLocal()
    
    try:
        # Create admin user if not exists
        admin_user = db.query(User).filter(User.email == "admin@vendotrash.com").first()
        if not admin_user:
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
            logger.info("✅ Created admin user: admin@vendotrash.com")
        else:
            logger.info("ℹ️  Admin user already exists")
        
        # Check if machine already exists
        existing_machine = db.query(Machine).filter(Machine.name == "VT-001").first()
        if not existing_machine:
            default_machine = Machine(
                name="VT-001",
                location="Building A - Ground Floor",
                status="Online",
                bin_capacity=100,
                total_collected=0
            )
            db.add(default_machine)
            logger.info("✅ Created default machine: VT-001")
        else:
            logger.info("ℹ️  Default machine already exists")
        
        # Check if rewards already exist
        existing_rewards = db.query(Reward).count()
        if existing_rewards == 0:
            rewards = [
                Reward(
                    name="Free Wi-Fi (1 hour)",
                    description="Get 1 hour of high-speed internet access",
                    points_required=20,
                    category="wifi",
                    is_active=True
                ),
                Reward(
                    name="Mobile Data (100MB)",
                    description="Receive 100MB mobile data for any network",
                    points_required=30,
                    category="data",
                    is_active=True
                ),
                Reward(
                    name="Local Store Voucher",
                    description="P50 voucher for partner local stores",
                    points_required=50,
                    category="voucher",
                    is_active=True
                ),
                Reward(
                    name="Premium Wi-Fi (1 day)",
                    description="Full day unlimited internet access",
                    points_required=80,
                    category="wifi",
                    is_active=True
                ),
                Reward(
                    name="Mobile Data (500MB)",
                    description="Receive 500MB mobile data for any network",
                    points_required=100,
                    category="data",
                    is_active=True
                ),
                Reward(
                    name="Premium Voucher",
                    description="P200 voucher for partner stores",
                    points_required=150,
                    category="voucher",
                    is_active=True
                ),
            ]
            
            for reward in rewards:
                db.add(reward)
            
            logger.info(f"✅ Created {len(rewards)} default rewards")
        else:
            logger.info(f"ℹ️  {existing_rewards} rewards already exist")
        
        db.commit()
        logger.info("✅ Database seeding completed!")
        
    except Exception as e:
        logger.error(f"❌ Error seeding database: {str(e)}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_database()

