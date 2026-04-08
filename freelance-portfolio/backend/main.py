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
allowed_origins_env = os.getenv("ALLOWED_ORIGINS", "*")
if allowed_origins_env == "*":
    origins = ["*"]
else:
    # Split by comma and strip whitespace to avoid issues
    origins = [origin.strip() for origin in allowed_origins_env.split(",") if origin.strip()]

# Note: When allow_origins=["*"], allow_credentials MUST be False
# To be safe in production, it's better to explicitly allow the origins
allow_credentials = False if "*" in origins else True

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=allow_credentials,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
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
async def contact_form_submit(form_data: ContactForm):
    print(f"DEBUG: Received contact form submission from {form_data.email}")
    
    if not mail_username or not mail_password:
        error_msg = "Email configuration is missing (MAIL_USERNAME or MAIL_PASSWORD)."
        print(f"DEBUG ERROR: {error_msg}")
        raise HTTPException(status_code=500, detail=error_msg)

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
        subtype="html"
    )

    fm = FastMail(conf)
    
    try:
        print(f"DEBUG: Attempting to send email to {mail_from}...")
        await fm.send_message(message)
        print("DEBUG SUCCESS: Email sent successfully!")
        return {"status": "success", "message": "Thank you for your message! We will get back to you soon."}
    except Exception as e:
        error_detail = str(e)
        print(f"DEBUG ERROR: Failed to send email: {error_detail}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Failed to send email: {error_detail}")

@app.get("/")
async def root():
    return {"message": "Echelon AI Solutions Portfolio Backend API is running."}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
