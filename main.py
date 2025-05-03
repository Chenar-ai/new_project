from fastapi import FastAPI
from routers import auth, user, roles, verify, career_type_router, service_router



app = FastAPI()

# Include the routers for authentication, user management, role management, and email verification
app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(user.router, prefix="/users", tags=["users"])
app.include_router(roles.router, prefix="/roles", tags=["roles"])
app.include_router(verify.router, prefix="/verify", tags=["verify"])
app.include_router(career_type_router.router, prefix="/admin", tags=["admin"])
app.include_router(service_router.router, prefix="/users", tags=["users"])
