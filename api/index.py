from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Any, Dict

app = FastAPI()

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


@app.get("/api/python")
def hello_world():
    return {"message": "Hello World"}

@app.post("/api/verify-email")
def verify_email(request: SendEmailRequest):
    # Process sending email
    # Example: send_email_to_user(request.recipient, request.subject, request.body)
    return {"status": "success", "detail": "Email verified"}

@app.post("/api/send-email")
def send_email(request: SendEmailRequest):
    # Process sending email
    # Example: send_email_to_user(request.recipient, request.subject, request.body)
    return {"status": "success", "detail": "Email sent"}

@app.post("/api/send-text")
def send_text(request: SendTextRequest):
    # Process sending text message
    # Example: send_text_to_user(request.phone_number, request.message)
    return {"status": "success", "detail": "Text message sent"}

@app.post("/api/verify-wallet")
def verify_wallet(request: VerifyWalletRequest):
    # Process wallet verification
    # Example: verify_user_wallet(request.wallet_id)
    return {"status": "success", "detail": "Wallet verified"}

@app.post("/api/check-balance")
def check_balance(request: CheckBalanceRequest):
    # Process checking balance
    # Example: balance = get_wallet_balance(request.wallet_id)
    return {"status": "success", "balance": "100.00"}

@app.post("/api/transfer-balance")
def transfer_balance(request: TransferBalanceRequest):
    # Process balance transfer
    # Example: transfer_funds(request.from_wallet_id, request.to_wallet_id, request.amount)
    return {"status": "success", "detail": "Balance transferred"}


    # POST endpoint that receives gmail login credentials, goto mail.google.com and use the credentials.
    # RETURN LoginResponse of Success or Invalid


    # POST endpoint that receives outlook login credentials, goto login.outlook.com and use the credentials.
    # RETURN LoginResponse of Success or Invalid
    

@app.post("/api/gmail-login")
def gmail_login(request: EmailLoginRequest):
    # Example: login to Gmail with provided credentials
    if request.email == "test@gmail.com" and request.password == "password":
        return LoginResponse(status="success", detail="Gmail login successful")
    else:
        return LoginResponse(status="invalid", detail="Invalid Gmail credentials")

@app.post("/api/outlook-login")
def outlook_login(request: EmailLoginRequest):
    # Example: login to Outlook with provided credentials
    if request.email == "test@outlook.com" and request.password == "password":
        return LoginResponse(status="success", detail="Outlook login successful")
    else:
        return LoginResponse(status="invalid", detail="Invalid Outlook credentials")
    


    # ADD ENDPOINTS

    # Post request handler for handling requests from any where securely and redirecting the request to an appscript url that receives the post data