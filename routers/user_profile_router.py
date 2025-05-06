from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from crud_operations import user_profile_crud
from schemas import UserProfileCreate, UserProfileUpdate, UserProfileResponse
from dependencies import get_current_user
from database import get_db

router = APIRouter()

# Create User Profile
@router.post("/profile/", response_model=UserProfileResponse)
def create_profile(profile: UserProfileCreate, db: Session = Depends(get_db), current_user: int = Depends(get_current_user)):
    return user_profile_crud.create_user_profile(db=db, user_id=current_user.id, user_profile=profile)

# Get User Profile
@router.get("/profile/", response_model=UserProfileResponse)
def get_profile(db: Session = Depends(get_db), current_user: int = Depends(get_current_user)):
    db_profile = user_profile_crud.get_user_profile(db=db, user_id=current_user.id)
    if db_profile is None:
        raise HTTPException(status_code=404, detail="Profile not found")
    return db_profile

# Update User Profile
@router.put("/profile/", response_model=UserProfileResponse)
def update_profile(profile: UserProfileUpdate, db: Session = Depends(get_db), current_user: int = Depends(get_current_user)):
    db_profile = user_profile_crud.update_user_profile(db=db, user_id=current_user.id, user_profile=profile)
    if db_profile is None:
        raise HTTPException(status_code=404, detail="Profile not found")
    return db_profile
