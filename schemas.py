from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime


class UserCreate(BaseModel):
    email: EmailStr
    full_name: str
    password: str

    class Config:
        from_attributes = True

class UserResponse(BaseModel):
    id: int
    email: EmailStr
    full_name: str
    is_active: bool
    is_verified: bool

    class Config:
        from_attributes = True




class ResetPasswordInput(BaseModel):
    token: str
    new_password: str


class ServiceCreate(BaseModel):
    name: str  # The name of the service
    description: str  # A description of the service
    price: float  # The price of the service (float for decimal values)
    category: str  # The category of the service
    career_type_id: int  # The ID of the career type the service belongs to
    currency: str = 'MYR'  # The currency/unit (e.g., USD, EUR, etc.)

    class Config:
        from_attributes = True  # Use from_attributes instead of orm_mode


class ServiceResponse(ServiceCreate):
    id: int  # The ID of the service
    user_id: int  # The ID of the user (service provider) who owns the service
    career_type_id: int  # The ID of the career type the service belongs to

    class Config:
        from_attributes = True  # Use from_attributes instead of orm_mode


class UserProfileCreate(BaseModel):
    name: str
    bio: Optional[str] = None
    phone_number: Optional[str] = None
    profile_picture: Optional[str] = None  # URL or path to the picture

    class Config:
        from_attributes = True

class UserProfileUpdate(BaseModel):
    name: Optional[str] = None
    bio: Optional[str] = None
    phone_number: Optional[str] = None
    profile_picture: Optional[str] = None  # URL or path to the picture

    class Config:
        from_attributes = True

class UserProfileResponse(BaseModel):
    id: int
    name: str
    bio: Optional[str] = None
    phone_number: Optional[str] = None
    profile_picture: Optional[str] = None

    class Config:
        from_attributes = True






class BookingCreate(BaseModel):
    user_id: int
    provider_id: int
    service_id: int
    booking_date: datetime  # Add this field to store the booking date
    reminder_time: datetime  # Optionally, you can include a reminder time if needed

    class Config:
        from_attributes = True



class BookingResponse(BaseModel):
    booking_id: int
    user_id: int
    provider_id: int
    service_id: int
    status: str  # Include status in the response
    booking_date: datetime
    service_details: Optional[str] = None
    payment_status: str  # Include payment_status in the response

    class Config:
        from_attributes = True




