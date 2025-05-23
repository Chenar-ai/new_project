from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from models import User
from utils import verify_token, log_activity
from database import get_db

router = APIRouter()


@router.get("/verify-email")
def verify_email(token: str, db: Session = Depends(get_db)):
    print(f"Received token: {token}")  # Log the token received
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
    log_activity(
        db=db,
        user_id=user.id,
        action="Email Verified",
        details=f"User {user.email} verified their email"
    )
    return {"message": "Email verified successfully"}
