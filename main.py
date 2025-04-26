from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from database import engine, Base, get_db
from models import User, Role
from schemas import UserCreate, UserResponse
from utils import (
    hash_password, verify_password, create_access_token, verify_token
)
from dependencies import role_required, get_current_user
from email_utils import send_verification_email
from fastapi import status
from fastapi import BackgroundTasks
from schemas import ResetPasswordInput
from datetime import timedelta
import os
from dotenv import load_dotenv
from email_utils import send_verification_email



# Initialize FastAPI app
app = FastAPI()

# Create tables in the database (if they don't exist already)
Base.metadata.create_all(bind=engine)

# OAuth2PasswordBearer instance
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

# Create user endpoint
@app.post("/users/", response_model=UserResponse)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.email == user.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed_pw = hash_password(user.password)
    new_user = User(
        email=user.email,
        full_name=user.full_name,
        hashed_password=hashed_pw
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    send_verification_email(new_user.email)
    return new_user

# Login and generate JWT token
@app.post("/login/")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == form_data.username).first()
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    if not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    if not user.is_verified:
        raise HTTPException(status_code=403, detail="Email not verified")

    # Create and return the JWT token
    access_token = create_access_token(
        data={"sub": user.email},
        roles=[role.name for role in user.roles]
    )
    return {"access_token": access_token, "token_type": "bearer"}

# Protected route to get current user info
@app.get("/users/me", response_model=UserResponse)
def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user

# Assign role to user
@app.post("/assign-role/")
def assign_role(email: str, role_name: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    role = db.query(Role).filter(Role.name == role_name).first()
    if not role:
        role = Role(name=role_name)
        db.add(role)
        try:
            db.commit()
        except IntegrityError:
            db.rollback()
            raise HTTPException(status_code=400, detail="Role creation failed")
        db.refresh(role)

    if role not in user.roles:
        user.roles.append(role)
        db.commit()

    return {"message": f"Role '{role_name}' assigned to user '{email}'"}

# Protected route for admin users only
@app.get("/admin-only/")
def read_admin_data(current_user: User = Depends(role_required(["admin"]))):
    return {"message": f"Hello Admin {current_user.full_name}"}

# Email verification endpoint
@app.get("/verify-email/")
def verify_email(token: str, db: Session = Depends(get_db)):
    payload = verify_token(token)
    if not payload:
        raise HTTPException(status_code=400, detail="Invalid or expired token")

    email = payload.get("sub")
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if user.is_verified:
        return {"message": "Email already verified"}

    user.is_verified = True
    db.commit()
    return {"message": "Email verified successfully"}


@app.post("/logout/", status_code=status.HTTP_200_OK)
def logout(current_user: User = Depends(get_current_user)):
    return {"message": "Successfully logged out. Please delete your token on the client side."}


load_dotenv()  # Make sure you load the .env file
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:7000")  # Default to localhost if not set

@app.post("/forgot-password")
def forgot_password(email: str, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(status_code=404, detail="Email not found")

    token = create_access_token(data={"sub": email}, expires_delta=timedelta(hours=1))
    reset_link = f"{FRONTEND_URL}/reset-password?token={token}"

    subject = "Reset your password"
    body = f"Click the link to reset your password: {reset_link}"

    # Send in background
    background_tasks.add_task(send_verification_email, user.email, subject, body)

    return {"message": "Password reset link sent to your email."}


@app.post("/reset-password")
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