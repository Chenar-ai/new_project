from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from models import User
from schemas import UserCreate, UserResponse, ResetPasswordInput
from database import get_db
from dependencies import get_current_user
from utils import hash_password, create_access_token, verify_token
from email_utils import send_password_reset_email
from datetime import timedelta
import os
from email_utils import send_verification_email
from urllib.parse import quote


router = APIRouter()

FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:9550")

@router.post("/users/")
def create_user(
    user_data: UserCreate,  # Assuming UserCreate is the schema for the user registration
    db: Session = Depends(get_db)
):
    # Check if the user already exists
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    # Create the new user and hash the password
    hashed_password = hash_password(user_data.password)
    new_user = User(
        email=user_data.email,
        full_name=user_data.full_name,
        hashed_password=hashed_password,
        is_verified=False  # User is not verified by default
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # Corrected: Pass a dictionary containing the email
    verification_token = create_access_token(data={"sub": new_user.email}, roles=[role.name for role in new_user.roles])

    # Generate the verification URL (this will be used by the user to verify their email)
    verification_url = f"{FRONTEND_URL}/verify/verify-email?token={quote(verification_token)}"

    send_verification_email(
        new_user.email,
        "Please verify your email address",  # Subject passed here
        f"Click the following link to verify your email: {verification_url}"  # Body passed here
    )

    return {"message": "User created successfully. Please check your email for the verification link."}

# **Get Current User**
@router.get("/users/me", response_model=UserResponse)
def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user

# **Forgot Password**
@router.post("/forgot-password")
def forgot_password(email: str, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    # Query to check if the user exists
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Generate the password reset token
    token = create_access_token(
        data={"sub": email},
        roles=user.roles,  # Ensure `roles` is a list, e.g. ["user"]
        expires_delta=timedelta(hours=1)
    )
    reset_link = f"{FRONTEND_URL}/reset-password?token={token}"

    # Send the password reset email in the background
    background_tasks.add_task(send_password_reset_email, user.email, "Reset your password", "")  # Updated task

    return {"message": "Password reset link sent to your email."}

# **Reset Password**
@router.post("/reset-password")
def reset_password(data: ResetPasswordInput, db: Session = Depends(get_db)):
    payload = verify_token(data.token)
    if not payload:
        raise HTTPException(status_code=400, detail="Invalid or expired token")

    email = payload.get("sub")
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.hashed_password = hash_password(data.new_password)
    db.commit()

    return {"message": "Password updated successfully"}
