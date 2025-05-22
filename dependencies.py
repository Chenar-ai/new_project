from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from database import get_db
from utils import verify_token
from models import User
from fastapi import Request

# OAuth2PasswordBearer instance to extract token from Authorization header
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

def get_current_user(
    request: Request,
    db: Session = Depends(get_db)
) -> User:
    # Try to get token from the cookie
    token = request.cookies.get("access_token")

    if not token:
        # Optionally check Authorization header fallback
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header[7:]

    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")

    payload = verify_token(token)  # Verify and decode the token
    if payload is None:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    user_email = payload.get("sub")  # Assuming 'sub' is the email in the token payload
    user = db.query(User).filter(User.email == user_email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if not user.is_verified:
        raise HTTPException(status_code=403, detail="Email not verified")

    return user

# Role check decorator
def role_required(required_roles: list[str]):
    def role_checker(current_user: User = Depends(get_current_user)):
        user_roles = [role.name for role in current_user.roles]
        if not any(role in user_roles for role in required_roles):
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        return current_user
    return role_checker


# Helper function to check if user has admin role (case-insensitive)
def admin_only(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)) -> User:
    # Ensure that the user has the admin role (case-insensitive)
    if not any(role.name.lower() == "admin" for role in current_user.roles):  # Convert to lowercase for comparison
        raise HTTPException(status_code=403, detail="Not authorized as admin")

    return current_user


