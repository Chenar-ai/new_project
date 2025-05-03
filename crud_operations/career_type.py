from sqlalchemy.orm import Session
from models import CareerType

# Create a new career type
def create_career_type(db: Session, name: str):
    db_career_type = CareerType(name=name)
    db.add(db_career_type)
    db.commit()
    db.refresh(db_career_type)
    return db_career_type

# Get all career types (for the admin to review)
def get_all_career_types(db: Session, skip: int = 0, limit: int = 100):
    return db.query(CareerType).offset(skip).limit(limit).all()

# Get career type by ID
def get_career_type_by_id(db: Session, career_type_id: int):
    return db.query(CareerType).filter(CareerType.id == career_type_id).first()

# Approve a career type
def approve_career_type(db: Session, career_type_id: int):
    db_career_type = db.query(CareerType).filter(CareerType.id == career_type_id).first()
    if db_career_type:
        db_career_type.is_approved = True
        db.commit()
        db.refresh(db_career_type)
    return db_career_type
