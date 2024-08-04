from fastapi import FastAPI, Query, HTTPException
from pydantic import BaseModel, EmailStr
import re
import httpx
import logging

# Initialize the FastAPI app
app = FastAPI()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SendEmailRequest(BaseModel):
    recipient: str
    subject: str
    body: str

class SendTextRequest(BaseModel):
    phone_number: str
    message: str

class VerifyWalletRequest(BaseModel):
    wallet_id: str

class CheckBalanceRequest(BaseModel):
    wallet_id: str

class TransferBalanceRequest(BaseModel):
    from_wallet_id: str
    to_wallet_id: str
    amount: float

class EmailLoginRequest(BaseModel):
    email: str
    password: str

class LoginResponse(BaseModel):
    status: str
    detail: str

class VerifyEmailResponse(BaseModel):
    email: str
    user: str
    domain: str
    status: str
    reason: str
    disposable: bool

@app.get("/api/python")
def hello_world():
    return {"message": "Hello World"}

def is_disposable_email(domain: str) -> bool:
    disposable_domains = ["mailinator.com", "trashmail.com", "tempmail.com"]  # Add more disposable domains here
    return domain in disposable_domains

@app.get("/api/verify-email", response_model=VerifyEmailResponse)
def verify_email(email: EmailStr = Query(..., description="The email address to verify")):
    logger.info(f"Starting verification for email: {email}")
    user, domain = email.split('@')

    # Check if the email format is valid
    if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
        logger.warning(f"Invalid email format: {email}")
        return VerifyEmailResponse(
            email=email,
            user=user,
            domain=domain,
            status="invalid",
            reason="Invalid email format",
            disposable=False
        )

    # Call the external API to verify the email
    api_url = f"https://headless-webfix.vercel.app/verify-email?email={email}"
    try:
        with httpx.Client(timeout=30.0) as client:  # Set a 30-second timeout
            response = client.get(api_url)
            response.raise_for_status()
            api_result = response.json()
            account_exists = api_result.get('account_exists', False)

        if account_exists:
            status = "valid"
            reason = "Email exists"
        else:
            status = "invalid"
            reason = "Email does not exist"

        return VerifyEmailResponse(
            email=email,
            user=user,
            domain=domain,
            status=status,
            reason=reason,
            disposable=is_disposable_email(domain)
        )
    except httpx.RequestError as e:
        logger.error(f"Error calling verification API: {e}")
        raise HTTPException(status_code=500, detail="Error verifying email")

@app.post("/api/send-email")
def send_email(request: SendEmailRequest):
    # Process sending email
    logger.info(f"Sending email to {request.recipient} with subject {request.subject}")
    return {"status": "success", "detail": "Email sent"}

@app.post("/api/send-text")
def send_text(request: SendTextRequest):
    # Process sending text message
    logger.info(f"Sending text to {request.phone_number}")
    return {"status": "success", "detail": "Text message sent"}

@app.post("/api/verify-wallet")
def verify_wallet(request: VerifyWalletRequest):
    # Process wallet verification
    logger.info(f"Verifying wallet ID {request.wallet_id}")
    return {"status": "success", "detail": "Wallet verified"}

@app.post("/api/check-balance")
def check_balance(request: CheckBalanceRequest):
    # Process checking balance
    logger.info(f"Checking balance for wallet ID {request.wallet_id}")
    return {"status": "success", "balance": "100.00"}

@app.post("/api/transfer-balance")
def transfer_balance(request: TransferBalanceRequest):
    # Process balance transfer
    logger.info(f"Transferring {request.amount} from wallet ID {request.from_wallet_id} to wallet ID {request.to_wallet_id}")
    return {"status": "success", "detail": "Balance transferred"}

@app.post("/api/gmail-login")
def gmail_login(request: EmailLoginRequest):
    # Example: login to Gmail with provided credentials
    logger.info(f"Attempting Gmail login for email {request.email}")
    if request.email == "test@gmail.com" and request.password == "password":
        return LoginResponse(status="success", detail="Gmail login successful")
    else:
        logger.warning(f"Invalid Gmail credentials for email {request.email}")
        return LoginResponse(status="invalid", detail="Invalid Gmail credentials")

@app.post("/api/outlook-login")
def outlook_login(request: EmailLoginRequest):
    # Example: login to Outlook with provided credentials
    logger.info(f"Attempting Outlook login for email {request.email}")
    if request.email == "test@outlook.com" and request.password == "password":
        return LoginResponse(status="success", detail="Outlook login successful")
    else:
        logger.warning(f"Invalid Outlook credentials for email {request.email}")
        return LoginResponse(status="invalid", detail="Invalid Outlook credentials")
