from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from db import get_db
from schemas import BookingCreate, BookingResponse
from controllers.booking_controller import create_booking, get_booking_by_id

router = APIRouter()


@router.post("/", response_model=BookingResponse)
def create_booking_route(booking_data: BookingCreate, db: Session = Depends(get_db)):
    """Create a new booking"""
    return create_booking(booking_data.dict(), db)


@router.get("/{booking_id}", response_model=BookingResponse)
def get_booking_route(booking_id: int, db: Session = Depends(get_db)):
    """Get booking by ID"""
    return get_booking_by_id(booking_id, db)

