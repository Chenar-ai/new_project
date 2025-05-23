from fastapi import APIRouter, Depends, HTTPException, Form
from sqlalchemy.orm import Session
from models import User, Role
from database import get_db
from crud_operations.user_crud import get_users, create_user, update_user, deactivate_user, get_logs  # Don't use create_user here
from dependencies import admin_only
from schemas import AdminUserCreate, UserResponse, ActivityLogResponse
from sqlalchemy import func
from email_utils import send_verification_email
from urllib.parse import quote
from utils import  create_access_token, log_activity
import os



router = APIRouter()

FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:9550")

# **List All Users** (Admin Only)
@router.get("/admin/users/")
def list_all_users(db: Session = Depends(get_db), current_user: User = Depends(admin_only)):
    users = get_users(db)
    return users

# **Create Admin User** (Admin Only)
@router.post("/admin/users/", response_model=UserResponse)
def create_admin_user(user: AdminUserCreate, db: Session = Depends(get_db), _current_user: User = Depends(admin_only)):
    # Ensure user does not exist already
    existing_user = db.query(User).filter(User.email == user.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    # Use the create_user function from users.py to handle user creation (general user registration)
    new_user = create_user(db, email=user.email, full_name=user.full_name, password=user.password)

    # Assign the admin role to the newly created user
    role = db.query(Role).filter(func.lower(Role.name) == "admin").first()
    if not role:
        raise HTTPException(status_code=404, detail="Admin role not found")
    new_user.roles.append(role)

    # Set the user's activation status to False initially (awaiting email verification)
    new_user.is_active = False

    # Commit user creation to the database but without activating them yet
    db.commit()
    db.refresh(new_user)

    # Create the email verification token
    verification_token = create_access_token(data={"sub": new_user.email}, roles=[role.name for role in new_user.roles])

    # Generate the verification URL
    verification_url = f"{FRONTEND_URL}/verify/verify-email?token={quote(verification_token)}"

    # Send the email verification link
    send_verification_email(
        new_user.email,
        "Please verify your email address",  # Subject
        f"Click the following link to verify your email: {verification_url}"  # Body
    )

    log_activity(
        db=db,
        user_id=_current_user.id,
        action="Create User",
        details=f"Created user {new_user.email} with role(s) {', '.join([r.name for r in new_user.roles])}"
    )

    # Return the newly created user with required fields as a response
    return UserResponse(
        id=new_user.id,
        email=new_user.email,
        full_name=new_user.full_name,
        is_active=new_user.is_active,
        is_verified=False  # Since the email is not verified yet
    )





def str_to_bool(value: str) -> bool:
    if value.lower() in {"true", "1", "yes", "on"}:
        return True
    elif value.lower() in {"false", "0", "no", "off"}:
        return False
    else:
        raise ValueError("Invalid boolean string")


@router.patch("/admin/users/{user_id}")
def update_admin_user(
    user_id: int,
    full_name: str = Form(None),
    email: str = Form(None),
    is_active: str = Form(None),  # Receive as string
    roles: list = Form(None),
    db: Session = Depends(get_db),
    _current_user: User = Depends(admin_only)
):
    if is_active is not None:
        try:
            is_active = str_to_bool(is_active)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid value for is_active")

    user = update_user(
        db=db,
        user_id=user_id,
        full_name=full_name,
        email=email,
        is_active=is_active,
        roles=roles
    )

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    log_activity(
        db=db,
        user_id=_current_user.id,
        action="Update User",
        details=f"Updated User {user.email} with role(s) {', '.join([r.name for r in user.roles])}"
    )


    return user




# **Deactivate User** (Admin Only)
@router.patch("/admin/users/{user_id}/deactivate")
def deactivate_user_route(user_id: int, db: Session = Depends(get_db), _current_user: User = Depends(admin_only)):
    user = deactivate_user(db=db, user_id=user_id)  # Using the deactivated function
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    log_activity(
        db=db,
        user_id=_current_user.id,
        action="Deactivate User",
        details=f"Deactivated User {user.email} with role(s) {', '.join([r.name for r in user.roles])}"
    )
    return {"message": "User deactivated successfully"}



# **Get User by ID** (Admin Only)
@router.get("/admin/users/{user_id}")
def get_user_by_id(user_id: int, db: Session = Depends(get_db), _current_user: User = Depends(admin_only)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.get("/admin/activity-logs", response_model=list[ActivityLogResponse])
def view_activity_logs(limit: int = 100, skip: int = 0, db: Session = Depends(get_db), _admin_user = Depends(admin_only)):
    logs = get_logs(db=db, limit=limit, skip=skip)
    return logs