from fastapi import APIRouter, Query, HTTPException
from pydantic import BaseModel, EmailStr
import logging

# Initialize the router
router = APIRouter()

# Configure logging
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

class VerifyEmailResponse(BaseModel):
    email: str
    user: str
    domain: str
    status: str
    reason: str
    disposable: bool

def is_disposable_email(domain: str) -> bool:
    disposable_domains = ["mailinator.com", "trashmail.com", "tempmail.com"]  # Add more disposable domains here
    return domain in disposable_domains

@router.get("/api/python")
def hello_world():
    return {"message": "Hello World"}

@router.post("/api/send-email")
def send_email(request: SendEmailRequest):
    # Process sending email
    logger.info(f"Sending email to {request.recipient} with subject {request.subject}")
    return {"status": "success", "detail": "Email sent"}

@router.post("/api/send-text")
def send_text(request: SendTextRequest):
    # Process sending text message
    logger.info(f"Sending text to {request.phone_number}")
    return {"status": "success", "detail": "Text message sent"}

@router.post("/api/verify-wallet")
def verify_wallet(request: VerifyWalletRequest):
    # Process wallet verification
    logger.info(f"Verifying wallet ID {request.wallet_id}")
    return {"status": "success", "detail": "Wallet verified"}

@router.post("/api/check-balance")
def check_balance(request: CheckBalanceRequest):
    # Process checking balance
    logger.info(f"Checking balance for wallet ID {request.wallet_id}")
    return {"status": "success", "balance": "100.00"}

@router.post("/api/transfer-balance")
def transfer_balance(request: TransferBalanceRequest):
    # Process balance transfer
    logger.info(f"Transferring {request.amount} from wallet ID {request.from_wallet_id} to wallet ID {request.to_wallet_id}")
    return {"status": "success", "detail": "Balance transferred"}
