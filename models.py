from sqlalchemy import Column, Integer, String, Boolean, DateTime, Table, ForeignKey, Float, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base

# Association table to link users with roles
user_roles = Table(
    'user_roles',
    Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id')),
    Column('role_id', Integer, ForeignKey('roles.id'))
)


# CareerType Model - New
class CareerType(Base):
    __tablename__ = 'career_types'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    is_approved = Column(Boolean, default=False)  # Admin approval flag

    def __repr__(self):
        return f"<CareerType(name={self.name})>"


# UserProfile Model - New
class UserProfile(Base):
    __tablename__ = 'user_profiles'

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), unique=True)
    name = Column(String, index=True)
    bio = Column(Text, nullable=True)
    profile_picture = Column(String, nullable=True)  # Path to the profile picture file
    phone_number = Column(String, nullable=True)

    user = relationship("User", back_populates="profile")

    def __repr__(self):
        return f"<UserProfile(user_id={self.user_id}, name={self.name})>"


# User Model - Updated with UserProfile relationship
class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    full_name = Column(String)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    roles = relationship("Role", secondary=user_roles, back_populates="users")
    services = relationship("Service", back_populates="user")
    profile = relationship("UserProfile", back_populates="user", uselist=False)  # One-to-one relationship

    def __repr__(self):
        return f"<User(email={self.email}, full_name={self.full_name})>"


# Role Model
class Role(Base):
    __tablename__ = 'roles'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True)

    users = relationship("User", secondary=user_roles, back_populates="roles")

    def __repr__(self):
        return f"<Role(name={self.name})>"


# Service Model - Updated with CareerType link
class Service(Base):
    __tablename__ = 'services'

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String, index=True)
    description = Column(Text)
    price = Column(Float)
    category = Column(String, index=True)
    currency = Column(String, default="USD")  # Store currency as a string
    user_id = Column(Integer, ForeignKey('users.id'))  # Foreign key to the User model
    career_type_id = Column(Integer, ForeignKey('career_types.id'))  # Foreign key to CareerType

    # Relationships
    user = relationship("User", back_populates="services")
    career_type = relationship("CareerType")

    def __repr__(self):
        return f"<Service(name={self.name}, category={self.category}, price={self.price}, currency={self.currency})>"
