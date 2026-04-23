from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
from typing import Optional, List
import os
import resend
from dotenv import load_dotenv

load_dotenv()

# Initialize Resend
resend_api_key = os.getenv("RESEND_API_KEY")
if resend_api_key:
    resend.api_key = resend_api_key
else:
    print("WARNING: RESEND_API_KEY is not set in environment variables.")

mail_from = os.getenv("MAIL_FROM", "onboarding@resend.dev")
mail_to = os.getenv("MAIL_TO", "echelonai.project@gmail.com")

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

# Email recipient (where the contact form notifications go)
mail_to = os.getenv("MAIL_TO", "echelonai.project@gmail.com")

class ContactForm(BaseModel):
    name: str
    email: EmailStr
    phone: Optional[str] = ""
    service: Optional[str] = ""
    message: str

@app.post("/api/contact")
async def contact_form_submit(form_data: ContactForm):
    print(f"DEBUG: Received contact form submission from {form_data.email}")
    
    if not resend_api_key:
        error_msg = "Resend API Key is missing."
        print(f"DEBUG ERROR: {error_msg}")
        raise HTTPException(status_code=500, detail=error_msg)

    # Prepare the email content
    html = f"""
    <h3>New Contact Form Submission</h3>
    <p><strong>Name:</strong> {form_data.name}</p>
    <p><strong>Email:</strong> {form_data.email}</p>
    <p><strong>Phone:</strong> {form_data.phone or 'N/A'}</p>
    <p><strong>Service of Interest:</strong> {form_data.service or 'N/A'}</p>
    <p><strong>Message:</strong></p>
    <p>{form_data.message}</p>
    """

    try:
        print(f"DEBUG: Attempting to send email via Resend to {mail_to}...")
        
        params = {
            "from": mail_from,
            "to": mail_to,
            "subject": f"New Contact from {form_data.name}",
            "html": html,
        }

        email = resend.Emails.send(params)
        print(f"DEBUG SUCCESS: Email sent successfully! ID: {email.get('id')}")
        
        return {"status": "success", "message": "Thank you for your message! We will get back to you soon."}
    except Exception as e:
        error_detail = str(e)
        print(f"DEBUG ERROR: Failed to send email: {error_detail}")
        raise HTTPException(status_code=500, detail=f"Failed to send email: {error_detail}")

@app.get("/")
async def root():
    return {"message": "Echelon AI Solutions Portfolio Backend API is running."}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
