from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from db import get_db
from schemas import MachineCreate, MachineResponse, PaginatedResponse
from controllers.machine_controller import (
    create_machine,
    get_all_machines,
    get_machine_by_id,
    update_machine_status
)

router = APIRouter()


@router.post("/", response_model=MachineResponse)
def create_machine_route(machine_data: MachineCreate, db: Session = Depends(get_db)):
    """Create a new machine (admin only)"""
    return create_machine(machine_data.model_dump(), db)


@router.get("/", response_model=PaginatedResponse[MachineResponse])
def get_machines_route(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    """Get all machines with pagination"""
    return get_all_machines(db, skip, limit)


@router.get("/{machine_id}", response_model=MachineResponse)
def get_machine_route(machine_id: int, db: Session = Depends(get_db)):
    """Get machine by ID"""
    return get_machine_by_id(machine_id, db)


@router.put("/{machine_id}/status", response_model=MachineResponse)
def update_machine_status_route(
    machine_id: int,
    status: str = Query(..., description="Status: Online, Offline, or Maintenance"),
    db: Session = Depends(get_db)
):
    """Update machine status (admin only)"""
    return update_machine_status(machine_id, status, db)

