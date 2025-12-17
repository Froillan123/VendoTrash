from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.orm import Session
from db import get_db
from schemas import RewardCreate, RewardResponse, RewardUpdate
from controllers.reward_controller import (
    create_reward,
    get_all_rewards,
    get_reward_by_id,
    update_reward
)

router = APIRouter()


@router.post("/", response_model=RewardResponse)
def create_reward_route(reward_data: RewardCreate, db: Session = Depends(get_db)):
    """Create a new reward (admin only)"""
    result = create_reward(reward_data.model_dump(), db)
    
    if isinstance(result, dict) and "error" in result:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result["error"]
        )
    
    return result


@router.get("/", response_model=list[RewardResponse])
def get_rewards_route(
    active_only: bool = Query(True, description="Only show active rewards"),
    db: Session = Depends(get_db)
):
    """Get available rewards catalog"""
    return get_all_rewards(db, active_only=active_only)


@router.get("/{reward_id}", response_model=RewardResponse)
def get_reward_route(reward_id: int, db: Session = Depends(get_db)):
    """Get reward by ID"""
    result = get_reward_by_id(reward_id, db)
    
    if isinstance(result, dict) and "error" in result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=result["error"]
        )
    
    return result


@router.put("/{reward_id}", response_model=RewardResponse)
def update_reward_route(
    reward_id: int,
    reward_data: RewardUpdate,
    db: Session = Depends(get_db)
):
    """Update reward (admin only)"""
    result = update_reward(reward_id, reward_data.model_dump(exclude_unset=True), db)
    
    if isinstance(result, dict) and "error" in result:
        if "not found" in result["error"].lower():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=result["error"]
            )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result["error"]
        )
    
    return result

