from fastapi import APIRouter
from pydantic import BaseModel
import logging

# Initialize the router
router = APIRouter()

# Configure logging
logger = logging.getLogger(__name__)

class EmailLoginRequest(BaseModel):
    email: str
    password: str

class LoginResponse(BaseModel):
    status: str
    detail: str

@router.post("/api/gmail-login")
def gmail_login(request: EmailLoginRequest):
    # Example: login to Gmail with provided credentials
    logger.info(f"Attempting Gmail login for email {request.email}")
    if request.email == "test@gmail.com" and request.password == "password":
        return LoginResponse(status="success", detail="Gmail login successful")
    else:
        logger.warning(f"Invalid Gmail credentials for email {request.email}")
        return LoginResponse(status="invalid", detail="Invalid Gmail credentials")

@router.post("/api/outlook-login")
def outlook_login(request: EmailLoginRequest):
    # Example: login to Outlook with provided credentials
    logger.info(f"Attempting Outlook login for email {request.email}")
    if request.email == "test@outlook.com" and request.password == "password":
        return LoginResponse(status="success", detail="Outlook login successful")
    else:
        logger.warning(f"Invalid Outlook credentials for email {request.email}")
        return LoginResponse(status="invalid", detail="Invalid Outlook credentials")
