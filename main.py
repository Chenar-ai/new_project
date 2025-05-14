from fastapi import FastAPI
from routers import auth, user, roles, verify, career_type_router
from routers import service_router, user_profile_router, booking_router
from sche import start_scheduler, stop_scheduler


# Define lifespan function to handle startup and shutdown events
async def lifespan(app: FastAPI):
    # Run startup tasks
    start_scheduler()  # Start the scheduler when the app starts

    # Yield control to FastAPI (this is where FastAPI starts handling requests)
    yield

    # Run shutdown tasks
    stop_scheduler()  # Stop the scheduler when the app shuts down


# Create FastAPI app with lifespan handler
app = FastAPI(lifespan=lifespan)

# Include the routers for authentication, user management, role management, and email verification
app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(user.router, prefix="/users", tags=["users"])
app.include_router(roles.router, prefix="/roles", tags=["roles"])
app.include_router(verify.router, prefix="/verify", tags=["verify"])
app.include_router(career_type_router.router, prefix="/admin", tags=["admin"])
app.include_router(service_router.router, prefix="/users", tags=["users"])
app.include_router(user_profile_router.router, prefix="/user-profile", tags=["user-profile"])
app.include_router(booking_router.router, prefix="/bookings", tags=["bookings"])
