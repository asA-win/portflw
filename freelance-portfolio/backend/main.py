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
# Use ALLOWED_ORIGINS from env or default to "*"
allowed_origins_env = os.getenv("ALLOWED_ORIGINS")
if allowed_origins_env:
    origins = allowed_origins_env.split(",")
else:
    origins = ["*"]

# Note: When allow_origins=["*"], allow_credentials MUST be False
allow_credentials = False if "*" in origins else True

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=allow_credentials,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Email Configuration
# Gmail Port 587 uses STARTTLS
# Gmail Port 465 uses SSL/TLS
mail_port = int(os.getenv("MAIL_PORT", 465))
mail_starttls_default = True if mail_port == 587 else False
mail_ssl_tls_default = True if mail_port == 465 else False

conf = ConnectionConfig(
    MAIL_USERNAME = os.getenv("MAIL_USERNAME"),
    MAIL_PASSWORD = os.getenv("MAIL_PASSWORD"),
    MAIL_FROM = os.getenv("MAIL_FROM", "echelonai.project@gmail.com"),
    MAIL_PORT = mail_port,
    MAIL_SERVER = os.getenv("MAIL_SERVER", "smtp.gmail.com"),
    MAIL_STARTTLS = os.getenv("MAIL_STARTTLS", str(mail_starttls_default)).lower() == "true",
    MAIL_SSL_TLS = os.getenv("MAIL_SSL_TLS", str(mail_ssl_tls_default)).lower() == "true",
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
    print(f"DEBUG: Received contact form submission from {form_data.email}")
    
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
    
    # Function to wrap email sending with logging
    async def send_email_with_logging(msg):
        try:
            await fm.send_message(msg)
            print("DEBUG: Email sent successfully!")
        except Exception as e:
            print(f"DEBUG ERROR: Failed to send email: {str(e)}")

    # Send email in the background
    background_tasks.add_task(send_email_with_logging, message)
    
    return {"status": "success", "message": "Thank you for your message! We will get back to you soon."}

@app.get("/")
async def root():
    return {"message": "Echelon AI Solutions Portfolio Backend API is running."}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
