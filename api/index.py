from fastapi import FastAPI, Query
from pydantic import BaseModel, EmailStr
import re
import dns.resolver
import smtplib
import time
import logging
import ssl

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

    # Check if the domain has MX records
    try:
        mx_records = dns.resolver.resolve(domain, 'MX')
        logger.info(f"MX records found for domain {domain}: {mx_records}")
    except (dns.resolver.NoAnswer, dns.resolver.NXDOMAIN) as e:
        logger.error(f"No MX records for domain {domain}: {e}")
        return VerifyEmailResponse(
            email=email,
            user=user,
            domain=domain,
            status="invalid",
            reason=f"No mail server for {email}",
            disposable=is_disposable_email(domain)
        )

    # Try to connect to the mail server with retries and alternative ports
    mail_server = str(mx_records[0].exchange)
    retries = 3
    timeout = 20  # Increased timeout
    smtp_ports = [587, 465]  # Common ports for SMTP submission

    for port in smtp_ports:
        for attempt in range(retries):
            try:
                logger.info(f"Attempting to connect to mail server {mail_server} on port {port}, attempt {attempt + 1}")
                if port == 587:
                    with smtplib.SMTP(mail_server, port, timeout=timeout) as server:
                        server.starttls()
                        server.helo()
                        server.mail('test@example.com')
                        code, message = server.rcpt(email)
                elif port == 465:
                    with smtplib.SMTP_SSL(mail_server, port, timeout=timeout) as server:
                        server.helo()
                        server.mail('test@example.com')
                        code, message = server.rcpt(email)
                
                if code == 250:
                    logger.info(f"Email {email} is deliverable")
                    return VerifyEmailResponse(
                        email=email,
                        user=user,
                        domain=domain,
                        status="valid",
                        reason="Email is deliverable",
                        disposable=is_disposable_email(domain)
                    )
                else:
                    logger.warning(f"Email {email} is undeliverable, SMTP code: {code}")
                    return VerifyEmailResponse(
                        email=email,
                        user=user,
                        domain=domain,
                        status="invalid",
                        reason="Email is undeliverable",
                        disposable=is_disposable_email(domain)
                    )
            except (smtplib.SMTPConnectError, smtplib.SMTPServerDisconnected, smtplib.SMTPException) as e:
                logger.error(f"Error connecting to mail server {mail_server} on port {port}: {e}")
                if attempt == retries - 1:
                    return VerifyEmailResponse(
                        email=email,
                        user=user,
                        domain=domain,
                        status="unknown",
                        reason=str(e),
                        disposable=is_disposable_email(domain)
                    )
                time.sleep(2)  # Wait before retrying
            except TimeoutError as e:
                logger.error(f"Connection to mail server {mail_server} on port {port} timed out: {e}")
                if attempt == retries - 1:
                    return VerifyEmailResponse(
                        email=email,
                        user=user,
                        domain=domain,
                        status="unknown",
                        reason="timed out",
                        disposable=is_disposable_email(domain)
                    )

@app.post("/api/send-email")
def send_email(request: SendEmailRequest):
    # Process sending email
    # Example: send_email_to_user(request.recipient, request.subject, request.body)
    logger.info(f"Sending email to {request.recipient} with subject {request.subject}")
    return {"status": "success", "detail": "Email sent"}

@app.post("/api/send-text")
def send_text(request: SendTextRequest):
    # Process sending text message
    # Example: send_text_to_user(request.phone_number, request.message)
    logger.info(f"Sending text to {request.phone_number}")
    return {"status": "success", "detail": "Text message sent"}

@app.post("/api/verify-wallet")
def verify_wallet(request: VerifyWalletRequest):
    # Process wallet verification
    # Example: verify_user_wallet(request.wallet_id)
    logger.info(f"Verifying wallet ID {request.wallet_id}")
    return {"status": "success", "detail": "Wallet verified"}

@app.post("/api/check-balance")
def check_balance(request: CheckBalanceRequest):
    # Process checking balance
    # Example: balance = get_wallet_balance(request.wallet_id)
    logger.info(f"Checking balance for wallet ID {request.wallet_id}")
    return {"status": "success", "balance": "100.00"}

@app.post("/api/transfer-balance")
def transfer_balance(request: TransferBalanceRequest):
    # Process balance transfer
    # Example: transfer_funds(request.from_wallet_id, request.to_wallet_id, request.amount)
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