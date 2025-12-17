from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.orm import Session
import uuid
from db import get_db
from dependencies import get_current_user
from models import User, Transaction
from schemas import TransactionCreate, TransactionResponse, PaginatedResponse
from controllers.transaction_controller import (
    create_transaction,
    get_transactions_by_user,
    get_transaction_by_id,
    get_all_transactions
)

router = APIRouter()


@router.post("/", response_model=TransactionResponse)
def create_transaction_route(
    transaction_data: TransactionCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new transaction (requires authentication)"""
    # Override user_id from token to prevent user from creating transactions for others
    transaction_dict = transaction_data.model_dump()
    transaction_dict["user_id"] = current_user.id
    
    result = create_transaction(transaction_dict, db)
    
    # Check for errors
    if isinstance(result, dict) and "error" in result:
        error_msg = result["error"].lower()
        if "not found" in error_msg:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=result["error"]
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result["error"]
            )
    
    return result


@router.get("/", response_model=PaginatedResponse[TransactionResponse])
def get_transactions_route(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=1000),
    all: str = Query("false", description="Get all transactions (admin only) - pass 'true'"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get transactions for current user or all transactions (admin only) with pagination"""
    # If admin requests all transactions
    if all.lower() == "true" and current_user.role == 'admin':
        return get_all_transactions(db, skip, limit)
    
    # Regular users get their own transactions (return as paginated response)
    transactions = get_transactions_by_user(current_user.id, db, skip, limit)
    from sqlalchemy import func
    total = db.query(func.count(Transaction.id)).filter(Transaction.user_id == current_user.id).scalar()
    return {
        "items": transactions,
        "total": total,
        "skip": skip,
        "limit": limit,
        "has_more": (skip + limit) < total
    }


@router.get("/{transaction_id}", response_model=TransactionResponse)
def get_transaction_route(transaction_id: str, db: Session = Depends(get_db)):
    """Get transaction by ID (UUID)"""
    try:
        transaction_uuid = uuid.UUID(transaction_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid transaction ID format"
        )
    result = get_transaction_by_id(transaction_uuid, db)
    
    if isinstance(result, dict) and "error" in result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=result["error"]
        )
    
    return result

