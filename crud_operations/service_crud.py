from sqlalchemy.orm import Session
from models import Service
from schemas import ServiceCreate  # The Pydantic model for incoming data

# Function to create a service
def create_service(db: Session, service: ServiceCreate, user_id: int):
    db_service = Service(
        name=service.name,
        description=service.description,
        price=service.price,
        category=service.category,
        user_id=user_id,  # The service provider
        career_type_id=service.career_type_id,  # The ID of the selected career type
        currency=service.currency  # The currency value (e.g., "MYR")
    )
    db.add(db_service)
    db.commit()
    db.refresh(db_service)
    return db_service


# Function to get all services with pagination
def get_services(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Service).offset(skip).limit(limit).all()

def get_service_by_id(db: Session, service_id: int):
    return db.query(Service).filter(Service.id == service_id).first()


def update_service(db: Session, service_id: int, service: ServiceCreate):
    db_service = db.query(Service).filter(Service.id == service_id).first()

    if db_service:
        db_service.name = service.name
        db_service.description = service.description
        db_service.price = service.price
        db_service.category = service.category
        db_service.currency = service.currency
        db_service.career_type_id = service.career_type_id
        db.commit()
        db.refresh(db_service)
        return db_service
    return None


def delete_service(db: Session, service_id: int):
    db_service = db.query(Service).filter(Service.id == service_id).first()

    if db_service:
        db.delete(db_service)
        db.commit()
        return db_service
    return None