from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.orm import Session
from db import get_db
from dependencies import get_current_user
from models import User
from schemas import RedemptionCreate, RedemptionResponse, PaginatedResponse
from controllers.redemption_controller import (
    create_redemption,
    get_redemptions_by_user,
    get_redemption_by_id,
    get_all_redemptions
)

router = APIRouter()


@router.post("/", response_model=RedemptionResponse)
def create_redemption_route(
    redemption_data: RedemptionCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new redemption (requires authentication)"""
    # Override user_id from token
    redemption_dict = redemption_data.model_dump()
    redemption_dict["user_id"] = current_user.id
    
    result = create_redemption(redemption_dict, db)
    
    # Check for errors and return appropriate HTTP status codes
    if isinstance(result, dict) and "error" in result:
        error_msg = result["error"].lower()
        if "insufficient" in error_msg or "not enough" in error_msg:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result["error"]
            )
        elif "not found" in error_msg:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=result["error"]
            )
        elif "not available" in error_msg or "inactive" in error_msg:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result["error"]
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result["error"]
            )
    
    return result


@router.get("/", response_model=PaginatedResponse[RedemptionResponse])
def get_redemptions_route(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=1000),
    all: str = Query("false", description="Get all redemptions (admin only) - pass 'true'"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get redemptions for current user or all redemptions (admin only) with pagination"""
    # If admin requests all redemptions
    if all.lower() == "true" and current_user.role == 'admin':
        return get_all_redemptions(db, skip, limit)
    
    # Regular users get their own redemptions (return as paginated response)
    from sqlalchemy import func
    from models import Redemption
    redemptions = get_redemptions_by_user(current_user.id, db, skip, limit)
    total = db.query(func.count(Redemption.id)).filter(Redemption.user_id == current_user.id).scalar()
    return {
        "items": redemptions,
        "total": total,
        "skip": skip,
        "limit": limit,
        "has_more": (skip + limit) < total
    }


@router.get("/{redemption_id}", response_model=RedemptionResponse)
def get_redemption_route(redemption_id: int, db: Session = Depends(get_db)):
    """Get redemption by ID"""
    result = get_redemption_by_id(redemption_id, db)
    
    if isinstance(result, dict) and "error" in result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=result["error"]
        )
    
    return result

