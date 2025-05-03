from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from crud_operations import service_crud  # Import the service CRUD operations
from schemas import ServiceCreate, ServiceResponse  # Import the Pydantic schemas for validation
from database import get_db
from dependencies import get_current_user  # To get the current user (service provider)

router = APIRouter()

# Create a new service
@router.post("/services/", response_model=ServiceResponse)
def create_service(
    service: ServiceCreate,  # This is the Pydantic schema
    db: Session = Depends(get_db),
    current_user: int = Depends(get_current_user)  # Current user from JWT token
):
    # Call the CRUD function to create the service
    db_service = service_crud.create_service(db=db, service=service, user_id=current_user.id)  # This should be a CRUD call, not a Pydantic method
    if db_service is None:
        raise HTTPException(status_code=400, detail="Service creation failed")
    return db_service

# Get all services
@router.get("/services/", response_model=list[ServiceResponse])
def get_services(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return service_crud.get_services(db=db, skip=skip, limit=limit)

# Get a service by ID
@router.get("/services/{service_id}", response_model=ServiceResponse)
def get_service(service_id: int, db: Session = Depends(get_db)):
    db_service = service_crud.get_service_by_id(db=db, service_id=service_id)
    if db_service is None:
        raise HTTPException(status_code=404, detail="Service not found")
    return db_service

# Update an existing service
@router.put("/services/{service_id}", response_model=ServiceResponse)
def update_service(service_id: int, service: ServiceCreate, db: Session = Depends(get_db)):
    db_service = service_crud.update_service(db=db, service_id=service_id, service=service)
    if db_service is None:
        raise HTTPException(status_code=404, detail="Service not found")
    return db_service

# Delete a service
@router.delete("/services/{service_id}")
def delete_service(service_id: int, db: Session = Depends(get_db)):
    db_service = service_crud.delete_service(db=db, service_id=service_id)
    if db_service is None:
        raise HTTPException(status_code=404, detail="Service not found")
    return {"message": "Service deleted successfully"}
