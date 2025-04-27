from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from models import User, Role
from database import get_db

router = APIRouter()

# **Assign Role to User**
@router.post("/assign-role/")
def assign_role(email: str, role_name: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    role = db.query(Role).filter(Role.name == role_name).first()
    if not role:
        role = Role(name=role_name)
        db.add(role)
        db.commit()
        db.refresh(role)

    if role not in user.roles:
        user.roles.append(role)
        db.commit()

    return {"message": f"Role '{role_name}' assigned to user '{email}'"}
