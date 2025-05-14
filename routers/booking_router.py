from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from datetime import timedelta
from database import get_db
from email_utils import send_booking_confirmation_email
from models import Booking, User, Service
from schemas import BookingCreate, BookingResponse
from sche import schedule_reminder_email  # Import the scheduler function

router = APIRouter()

@router.post("/bookings/", status_code=201)
async def create_booking(
        booking_details: BookingCreate,
        background_tasks: BackgroundTasks,
        db: Session = Depends(get_db)
):
    # Fetch the user, provider, and service from the database
    user = db.query(User).filter(User.id == booking_details.user_id).first()
    provider = db.query(User).filter(User.id == booking_details.provider_id).first()
    service = db.query(Service).filter(Service.id == booking_details.service_id).first()

    # Check if the user, provider, or service does not exist
    if not user or not provider or not service:
        raise HTTPException(status_code=404, detail="User, Provider, or Service not found")

    # Calculate the reminder time (1 day before the booking date)
    reminder_time = booking_details.booking_date - timedelta(days=1)

    # Create new booking
    new_booking = Booking(
        booking_date=booking_details.booking_date,
        reminder_time=reminder_time,  # Use the calculated reminder time
        user_id=booking_details.user_id,
        provider_id=booking_details.provider_id,
        service_id=booking_details.service_id
    )

    db.add(new_booking)
    db.commit()

    # Refresh the new booking object to load relationships
    db.refresh(new_booking)  # Ensure relationships are loaded

    # Prepare the booking details for the reminder email
    booking_details_dict = {
        "customer_email": user.email,
        "user_full_name": user.full_name,
        "provider_full_name": provider.full_name,
        "service_name": service.name,
        "booking_date": new_booking.booking_date,
        "id": new_booking.id,
        "user_id": booking_details.user_id,  # Add user_id for later use
        "provider_id": booking_details.provider_id,  # Add provider_id for later use
        "service_id": booking_details.service_id,  # Add service_id for later use
    }

    send_booking_confirmation_email(user.email, "Booking Confirmation", new_booking)

    # Schedule the reminder email
    schedule_reminder_email(booking_details_dict, reminder_time)

    # Return the new booking object
    return new_booking




# Get all bookings for a specific user (customer)
@router.get("/bookings/{user_id}", response_model=list[BookingResponse])
def get_bookings(user_id: int, db: Session = Depends(get_db)):
    bookings = db.query(Booking).filter(Booking.user_id == user_id).all()
    if not bookings:
        raise HTTPException(status_code=404, detail="No bookings found")
    return bookings

# Update booking status
@router.patch("/bookings/{booking_id}", response_model=BookingResponse)
def update_booking_status(
        booking_id: int,
        status: str = None,  # Optional, only update if provided
        payment_status: str = None,  # Optional, only update if provided
        db: Session = Depends(get_db)
):
    db_booking = db.query(Booking).filter(Booking.booking_id == booking_id).first()

    if not db_booking:
        raise HTTPException(status_code=404, detail="Booking not found")

    # Update booking status if provided
    if status:
        db_booking.status = status

    # Update payment status if provided
    if payment_status:
        db_booking.payment_status = payment_status

    db.commit()
    db.refresh(db_booking)
    return db_booking
