from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
from typing import Optional, List
import os
from dotenv import load_dotenv
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType

load_dotenv()

app = FastAPI()

# Configure CORS
# Use "*" to allow all origins during development, especially when opening files directly via file://
origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Email Configuration
# Note: For Gmail, you should use an "App Password" rather than your regular password.
conf = ConnectionConfig(
    MAIL_USERNAME = os.getenv("MAIL_USERNAME"),
    MAIL_PASSWORD = os.getenv("MAIL_PASSWORD"),
    MAIL_FROM = os.getenv("MAIL_FROM", "echelonai.project@gmail.com"),
    MAIL_PORT = int(os.getenv("MAIL_PORT", 465)),
    MAIL_SERVER = os.getenv("MAIL_SERVER", "smtp.gmail.com"),
    MAIL_STARTTLS = False,
    MAIL_SSL_TLS = True,
    USE_CREDENTIALS = True,
    VALIDATE_CERTS = True
)

class ContactForm(BaseModel):
    name: str
    email: EmailStr
    service: Optional[str] = None
    message: str

@app.post("/api/contact")
async def contact_form_submit(form_data: ContactForm, background_tasks: BackgroundTasks):
    # Prepare the email content
    html = f"""
    <h3>New Contact Form Submission</h3>
    <p><strong>Name:</strong> {form_data.name}</p>
    <p><strong>Email:</strong> {form_data.email}</p>
    <p><strong>Service of Interest:</strong> {form_data.service or 'N/A'}</p>
    <p><strong>Message:</strong></p>
    <p>{form_data.message}</p>
    """

    message = MessageSchema(
        subject=f"New Contact from {form_data.name}",
        recipients=["echelonai.project@gmail.com"],
        body=html,
        subtype=MessageType.html
    )

    fm = FastMail(conf)
    
    # Send email in the background to avoid blocking the response
    background_tasks.add_task(fm.send_message, message)
    
    return {"status": "success", "message": "Thank you for your message! We will get back to you soon."}

@app.get("/")
async def root():
    return {"message": "Echelon AI Solutions Portfolio Backend API is running."}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
