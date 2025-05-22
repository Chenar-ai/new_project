from sqlalchemy.orm import Session
from models import User, Role
from passlib.context import CryptContext

# Password hashing setup
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")  # Fixed the parenthesis

# Hash the password
def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def create_user(db: Session, email: str, full_name: str, password: str, roles: list = None):
    hashed_password = hash_password(password)
    db_user = User(email=email, full_name=full_name, hashed_password=hashed_password)

    # Assign roles if provided
    if roles:
        db_user.roles = db.query(Role).filter(Role.name.in_(roles)).all()

    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


# Get All Users
def get_users(db: Session):
    return db.query(User).all()


# Get User by ID
def get_user_by_id(db: Session, user_id: int):
    return db.query(User).filter(User.id == user_id).first()


def update_user(db: Session, user_id: int, full_name: str = None, email: str = None, is_active: bool = None,
                roles: list = None):
    db_user = db.query(User).filter(User.id == user_id).first()

    if db_user:
        if full_name:
            db_user.full_name = full_name
        if email:
            db_user.email = email
        if is_active is not None:
            db_user.is_active = is_active

        if roles is not None:  # Only update roles if provided
            # Clear existing roles and add the new ones
            db_user.roles.clear()
            for role_name in roles:
                role = db.query(Role).filter(Role.name == role_name).first()
                if role:
                    db_user.roles.append(role)

        db.commit()
        db.refresh(db_user)
        return db_user
    return None


def deactivate_user(db: Session, user_id: int):
    db_user = db.query(User).filter(User.id == user_id).first()
    if db_user:
        db_user.is_active = False
        db.commit()
        db.refresh(db_user)
        return db_user
    return None

