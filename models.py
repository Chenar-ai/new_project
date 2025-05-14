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

    # models.py


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
    bookings_as_customer = relationship("Booking", back_populates="user",
                                        foreign_keys="[Booking.user_id]")  # Customer bookings
    bookings_as_provider = relationship("Booking", back_populates="provider",
                                        foreign_keys="[Booking.provider_id]")  # Provider bookings

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


# models.py

class Service(Base):
    __tablename__ = 'services'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    description = Column(String)
    price = Column(Float)
    category = Column(String)
    user_id = Column(Integer, ForeignKey('users.id'))

    user = relationship("User", back_populates="services")
    bookings = relationship("Booking", back_populates="service")  # Add this line

    def __repr__(self):
        return f"<Service(name={self.name}, description={self.description})>"



# models.py

class Booking(Base):
    __tablename__ = 'bookings'

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    provider_id = Column(Integer, ForeignKey('users.id'))
    service_id = Column(Integer, ForeignKey('services.id'))
    booking_date = Column(DateTime)
    reminder_time = Column(DateTime)

    user = relationship("User", back_populates="bookings_as_customer", foreign_keys=[user_id])
    provider = relationship("User", back_populates="bookings_as_provider", foreign_keys=[provider_id])
    service = relationship("Service", back_populates="bookings")

    def __repr__(self):
        return f"<Booking(user_id={self.user_id}, provider_id={self.provider_id}, service_id={self.service_id})>"

    @property
    def customer_email(self):
        return self.user.email  # Assuming the user is the customer

    @property
    def provider_email(self):
        return self.provider.email  # Assuming the provider is also a User
