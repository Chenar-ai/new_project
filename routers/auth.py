from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm
from database import get_db
from models import User
from utils import verify_password, create_access_token
import os
from dependencies import get_current_user




router = APIRouter()
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:7070")

# **Login Route**
@router.post("/login/")
def login(
    response: Response,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.email == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    if not user.is_verified:
        raise HTTPException(status_code=403, detail="Email not verified")

    access_token = create_access_token(
        data={"sub": user.email},
        roles=[role.name for role in user.roles]
    )

    # Set the token as a cookie
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        max_age=3600,  # 1 hour
        samesite="Lax",  # Adjust if using cross-origin frontend
        secure=False     # Set True if using HTTPS
    )

    return {"message": "Login successful"}


@router.post("/logout")
def logout(response: Response, user: User = Depends(get_current_user)):
    response.delete_cookie("access_token")
    return {"message": f"User {user.email} successfully logged out"}