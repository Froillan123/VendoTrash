from sqlalchemy.orm import Session
from models import Reward
from schemas import RewardResponse


def create_reward(data: dict, db: Session):
    """Create a new reward - business logic"""
    new_reward = Reward(
        name=data["name"],
        description=data.get("description"),
        points_required=data["points_required"],
        category=data["category"],
        is_active=data.get("is_active", True)
    )
    
    db.add(new_reward)
    db.commit()
    db.refresh(new_reward)
    
    return RewardResponse.model_validate(new_reward)


def get_all_rewards(db: Session, active_only: bool = True):
    """Get all rewards - business logic"""
    query = db.query(Reward)
    if active_only:
        query = query.filter(Reward.is_active == True)
    
    rewards = query.all()
    return [RewardResponse.model_validate(r) for r in rewards]


def get_reward_by_id(reward_id: int, db: Session):
    """Get reward by ID - business logic"""
    reward = db.query(Reward).filter(Reward.id == reward_id).first()
    
    if not reward:
        return {"error": "Reward not found"}
    
    return RewardResponse.model_validate(reward)


def update_reward(reward_id: int, data: dict, db: Session):
    """Update reward - business logic"""
    reward = db.query(Reward).filter(Reward.id == reward_id).first()
    
    if not reward:
        return {"error": "Reward not found"}
    
    if "name" in data:
        reward.name = data["name"]
    if "description" in data:
        reward.description = data["description"]
    if "points_required" in data:
        reward.points_required = data["points_required"]
    if "category" in data:
        reward.category = data["category"]
    if "is_active" in data:
        reward.is_active = data["is_active"]
    
    db.commit()
    db.refresh(reward)
    
    return RewardResponse.model_validate(reward)

