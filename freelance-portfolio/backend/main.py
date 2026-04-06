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
mail_port = int(os.getenv("MAIL_PORT", 587))
mail_server = os.getenv("MAIL_SERVER", "smtp.gmail.com")
mail_username = os.getenv("MAIL_USERNAME")
mail_password = os.getenv("MAIL_PASSWORD")
mail_from = os.getenv("MAIL_FROM", mail_username or "echelonai.project@gmail.com")

# Improved logic for STARTTLS vs SSL/TLS
# Port 587: STARTTLS = True, SSL_TLS = False
# Port 465: STARTTLS = False, SSL_TLS = True
is_port_587 = mail_port == 587
mail_starttls = os.getenv("MAIL_STARTTLS", "True" if is_port_587 else "False").lower() == "true"
mail_ssl_tls = os.getenv("MAIL_SSL_TLS", "False" if is_port_587 else "True").lower() == "true"

conf = ConnectionConfig(
    MAIL_USERNAME = mail_username,
    MAIL_PASSWORD = mail_password,
    MAIL_FROM = mail_from,
    MAIL_PORT = mail_port,
    MAIL_SERVER = mail_server,
    MAIL_STARTTLS = mail_starttls,
    MAIL_SSL_TLS = mail_ssl_tls,
    USE_CREDENTIALS = True,
    VALIDATE_CERTS = False  # Changed to False to avoid common certificate verification issues
)

class ContactForm(BaseModel):
    name: str
    email: EmailStr
    service: Optional[str] = ""
    message: str

@app.post("/api/contact")
async def contact_form_submit(form_data: ContactForm, background_tasks: BackgroundTasks):
    print(f"DEBUG: Received contact form submission from {form_data.email}")
    print(f"DEBUG: Email Config: Server={mail_server}, Port={mail_port}, User={mail_username}, From={mail_from}, STARTTLS={mail_starttls}, SSL_TLS={mail_ssl_tls}")
    
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
        recipients=[mail_from],  # Send to the configured MAIL_FROM address (your email)
        body=html,
        subtype="html"  # Use string for better compatibility across fastapi-mail versions
    )

    fm = FastMail(conf)
    
    # Function to wrap email sending with logging
    async def send_email_with_logging(msg):
        try:
            print(f"DEBUG: Attempting to send email to {msg.recipients}...")
            await fm.send_message(msg)
            print("DEBUG SUCCESS: Email sent successfully!")
        except Exception as e:
            print(f"DEBUG ERROR: Failed to send email: {str(e)}")
            import traceback
            traceback.print_exc()

    # Send email in the background
    background_tasks.add_task(send_email_with_logging, message)
    
    return {"status": "success", "message": "Thank you for your message! We will get back to you soon."}

@app.get("/")
async def root():
    return {"message": "Echelon AI Solutions Portfolio Backend API is running."}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
