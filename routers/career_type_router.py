from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from crud_operations import career_type  # Import CRUD functions
from database import get_db

router = APIRouter()

@router.post("/career_types/")
def create_career_type(name: str, db: Session = Depends(get_db)):
    return career_type.create_career_type(db=db, name=name)

@router.get("/career_types/")
def get_career_types(db: Session = Depends(get_db)):
    return career_type.get_all_career_types(db=db)

@router.put("/career_types/{career_type_id}/approve")
def approve_career_type(career_type_id: int, db: Session = Depends(get_db)):
    db_career_type = career_type.approve_career_type(db=db, career_type_id=career_type_id)
    if db_career_type is None:
        raise HTTPException(status_code=404, detail="Career type not found")
    return {"message": f"Career type {db_career_type.name} approved"}



import logging
logging.basicConfig(level=logging.DEBUG)

logger = logging.getLogger(__name__)
logger.debug("Career Type Router Loaded")
