from sqlalchemy.orm import Session
from models import UserProfile
from schemas import UserProfileCreate, UserProfileUpdate

# Function to create a user profile
def create_user_profile(db: Session, user_id: int, user_profile: UserProfileCreate):
    db_profile = UserProfile(user_id=user_id, **user_profile.dict())
    db.add(db_profile)
    db.commit()
    db.refresh(db_profile)
    return db_profile

# Function to get a user profile by user_id
def get_user_profile(db: Session, user_id: int):
    return db.query(UserProfile).filter(UserProfile.user_id == user_id).first()

# Function to update a user profile
def update_user_profile(db: Session, user_id: int, user_profile: UserProfileUpdate):
    db_profile = db.query(UserProfile).filter(UserProfile.user_id == user_id).first()
    if db_profile:
        for key, value in user_profile.dict().items():
            setattr(db_profile, key, value)
        db.commit()
        db.refresh(db_profile)
        return db_profile
    return None
