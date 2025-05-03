from pydantic import BaseModel, EmailStr


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
