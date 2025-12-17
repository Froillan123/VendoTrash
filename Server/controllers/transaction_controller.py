from sqlalchemy.orm import Session, joinedload
from sqlalchemy.sql import func
from models import Transaction, User, Machine
from schemas import TransactionResponse


def create_transaction(data: dict, db: Session):
    """Create a new transaction - business logic"""
    # Get user and machine
    user = db.query(User).filter(User.id == data["user_id"]).first()
    machine = db.query(Machine).filter(Machine.id == data["machine_id"]).first()
    
    if not user:
        return {"error": "User not found"}
    
    if not machine:
        return {"error": "Machine not found"}
    
    # Create transaction
    new_transaction = Transaction(
        user_id=data["user_id"],
        machine_id=data["machine_id"],
        material_type=data["material_type"],
        points_earned=data["points_earned"],
        status="Completed"
    )
    
    db.add(new_transaction)
    
    # Update user stats
    user.total_points += data["points_earned"]
    user.total_transactions += 1
    if data["material_type"] == "PLASTIC":
        user.total_plastic += 1
    elif data["material_type"] == "NON_PLASTIC":
        user.total_metal += 1
    
    # Update machine stats
    machine.total_collected += 1
    machine.last_activity = db.query(func.now()).scalar()
    
    db.commit()
    db.refresh(new_transaction)
    
    return TransactionResponse.model_validate(new_transaction)


def get_transactions_by_user(user_id: int, db: Session, skip: int = 0, limit: int = 100):
    """Get transactions for a user - business logic"""
    transactions = db.query(Transaction).options(
        joinedload(Transaction.user),
        joinedload(Transaction.machine)
    ).filter(
        Transaction.user_id == user_id
    ).order_by(Transaction.created_at.desc()).offset(skip).limit(limit).all()
    
    return [TransactionResponse.model_validate(t) for t in transactions]


def get_transaction_by_id(transaction_id, db: Session):
    """Get transaction by ID (UUID) - business logic"""
    transaction = db.query(Transaction).filter(Transaction.id == transaction_id).first()
    
    if not transaction:
        return {"error": "Transaction not found"}
    
    return TransactionResponse.model_validate(transaction)


def get_all_transactions(db: Session, skip: int = 0, limit: int = 100):
    """Get all transactions - business logic (admin only)"""
    transactions = db.query(Transaction).options(
        joinedload(Transaction.user),
        joinedload(Transaction.machine)
    ).order_by(Transaction.created_at.desc()).offset(skip).limit(limit).all()
    total = db.query(func.count(Transaction.id)).scalar()
    return {
        "items": [TransactionResponse.model_validate(t) for t in transactions],
        "total": total,
        "skip": skip,
        "limit": limit,
        "has_more": (skip + limit) < total
    }

