from sqlalchemy.orm import Session
from sqlalchemy import func
from models import Machine
from schemas import MachineResponse
from datetime import datetime


def create_machine(data: dict, db: Session):
    """Create a new machine - business logic"""
    # Check if machine name already exists
    existing = db.query(Machine).filter(Machine.name == data["name"]).first()
    if existing:
        return {"error": "Machine name already exists"}
    
    new_machine = Machine(
        name=data["name"],
        location=data["location"],
        bin_capacity=data.get("bin_capacity", 100),
        status="Online"
    )
    
    db.add(new_machine)
    db.commit()
    db.refresh(new_machine)
    
    return MachineResponse.model_validate(new_machine)


def get_all_machines(db: Session, skip: int = 0, limit: int = 100):
    """Get all machines - business logic"""
    machines = db.query(Machine).order_by(Machine.created_at.desc()).offset(skip).limit(limit).all()
    total = db.query(func.count(Machine.id)).scalar()
    return {
        "items": [MachineResponse.model_validate(m) for m in machines],
        "total": total,
        "skip": skip,
        "limit": limit,
        "has_more": (skip + limit) < total
    }


def get_machine_by_id(machine_id: int, db: Session):
    """Get machine by ID - business logic"""
    machine = db.query(Machine).filter(Machine.id == machine_id).first()
    
    if not machine:
        return {"error": "Machine not found"}
    
    return MachineResponse.model_validate(machine)


def update_machine_status(machine_id: int, status: str, db: Session):
    """Update machine status - business logic"""
    machine = db.query(Machine).filter(Machine.id == machine_id).first()
    
    if not machine:
        return {"error": "Machine not found"}
    
    valid_statuses = ["Online", "Offline", "Maintenance"]
    if status not in valid_statuses:
        return {"error": f"Invalid status. Must be one of: {', '.join(valid_statuses)}"}
    
    machine.status = status
    machine.last_activity = db.query(func.now()).scalar()
    
    db.commit()
    db.refresh(machine)
    
    return MachineResponse.model_validate(machine)

