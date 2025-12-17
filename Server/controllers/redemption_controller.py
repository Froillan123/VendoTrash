from sqlalchemy.orm import Session, joinedload
from models import Redemption, User, Reward
from schemas import RedemptionResponse


def create_redemption(data: dict, db: Session):
    """Create a new redemption - business logic"""
    # Get user and reward
    user = db.query(User).filter(User.id == data["user_id"]).first()
    reward = db.query(Reward).filter(Reward.id == data["reward_id"]).first()
    
    if not user:
        return {"error": "User not found"}
    
    if not reward:
        return {"error": "Reward not found"}
    
    if not reward.is_active:
        return {"error": "Reward is not available"}
    
    # Check if user has enough points
    if user.total_points < data["points_used"]:
        return {"error": "Insufficient points"}
    
    # Verify points match reward requirement
    if data["points_used"] != reward.points_required:
        return {"error": "Points used must match reward requirement"}
    
    # Create redemption
    new_redemption = Redemption(
        user_id=data["user_id"],
        reward_id=data["reward_id"],
        points_used=data["points_used"],
        status="Completed"
    )
    
    db.add(new_redemption)
    
    # Deduct points from user
    user.total_points -= data["points_used"]
    
    db.commit()
    db.refresh(new_redemption)
    
    # Reload with reward relationship
    db.refresh(new_redemption)
    redemption_with_reward = db.query(Redemption).options(
        joinedload(Redemption.reward)
    ).filter(Redemption.id == new_redemption.id).first()
    
    return RedemptionResponse.model_validate(redemption_with_reward)


def get_redemptions_by_user(user_id: int, db: Session, skip: int = 0, limit: int = 100):
    """Get redemptions for a user - business logic"""
    redemptions = db.query(Redemption).options(
        joinedload(Redemption.reward)
    ).filter(
        Redemption.user_id == user_id
    ).order_by(Redemption.created_at.desc()).offset(skip).limit(limit).all()
    
    return [RedemptionResponse.model_validate(r) for r in redemptions]


def get_redemption_by_id(redemption_id: int, db: Session):
    """Get redemption by ID - business logic"""
    redemption = db.query(Redemption).options(
        joinedload(Redemption.reward)
    ).filter(Redemption.id == redemption_id).first()
    
    if not redemption:
        return {"error": "Redemption not found"}
    
    return RedemptionResponse.model_validate(redemption)


def get_all_redemptions(db: Session, skip: int = 0, limit: int = 100):
    """Get all redemptions - business logic (admin only)"""
    from sqlalchemy import func
    redemptions = db.query(Redemption).options(
        joinedload(Redemption.reward)
    ).order_by(Redemption.created_at.desc()).offset(skip).limit(limit).all()
    
    total = db.query(func.count(Redemption.id)).scalar()
    return {
        "items": [RedemptionResponse.model_validate(r) for r in redemptions],
        "total": total,
        "skip": skip,
        "limit": limit,
        "has_more": (skip + limit) < total
    }

