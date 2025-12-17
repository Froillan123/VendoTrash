from sqlalchemy.orm import Session
from models import Booking
from schemas import BookingResponse


def create_booking(data: dict, db: Session):
    """Create a new booking - business logic"""
    new_booking = Booking(
        user_id=data["user_id"],
        title=data["title"],
        description=data.get("description"),
        status="pending"
    )
    
    db.add(new_booking)
    db.commit()
    db.refresh(new_booking)
    
    return BookingResponse.model_validate(new_booking)


def get_booking_by_id(booking_id: int, db: Session):
    """Get booking by ID - business logic"""
    booking = db.query(Booking).filter(Booking.id == booking_id).first()
    
    if not booking:
        return {"error": "Booking not found"}
    
    return BookingResponse.model_validate(booking)

