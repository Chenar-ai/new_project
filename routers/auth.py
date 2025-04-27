from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, status
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm
from database import get_db
from models import User
from utils import hash_password, verify_password, create_access_token, verify_token
from email_utils import send_verification_email
from datetime import timedelta
import os
from dependencies import get_current_user


router = APIRouter()
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:7000")

# **Login Route**
@router.post("/login/")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    if not user.is_verified:
        raise HTTPException(status_code=403, detail="Email not verified")

    access_token = create_access_token(
        data={"sub": user.email},
        roles=[role.name for role in user.roles]
    )
    return {"access_token": access_token, "token_type": "bearer"}

# **Logout Route**
@router.post("/logout/", status_code=status.HTTP_200_OK)
def logout(current_user: User = Depends(get_current_user)):
    return {"message": "Successfully logged out. Please delete your token on the client side."}
