import random
import string
import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
import bcrypt

# Password hashing (direct bcrypt — avoids passlib + bcrypt 5.x incompatibility)
def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(plain: str, hashed: str) -> bool:
    return bcrypt.checkpw(plain.encode('utf-8'), hashed.encode('utf-8'))

# OTP
def generate_otp() -> str:
    return ''.join(random.choices(string.digits, k=6))

def otp_expiry() -> datetime:
    return datetime.utcnow() + timedelta(minutes=5)

def is_otp_valid(expiry: datetime) -> bool:
    if expiry is None:
        return False
    return datetime.utcnow() <= expiry

# Email sending
SMTP_EMAIL = os.getenv("SMTP_EMAIL", "")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")

def send_otp_email(to_email: str, otp: str) -> bool:
    """Send OTP via Gmail SMTP. Returns True if sent, False otherwise."""
    if not SMTP_EMAIL or not SMTP_PASSWORD:
        print(f"[OTP] Email not configured. OTP for {to_email}: {otp}")
        return False

    try:
        msg = MIMEMultipart()
        msg["From"] = SMTP_EMAIL
        msg["To"] = to_email
        msg["Subject"] = "Civic Monitor — Your Verification Code"

        body = f"""
        <html>
        <body style="font-family: Arial, sans-serif; background: #0d1117; color: #f1f5f9; padding: 40px;">
            <div style="max-width: 400px; margin: 0 auto; background: rgba(255,255,255,0.05); border-radius: 16px; padding: 40px; border: 1px solid rgba(255,255,255,0.1);">
                <h2 style="text-align: center; color: #818cf8;">🏛️ Civic Monitor</h2>
                <p style="text-align: center; color: #94a3b8;">Your verification code is:</p>
                <div style="text-align: center; font-size: 36px; font-weight: 900; letter-spacing: 12px; color: #6366f1; padding: 20px; background: rgba(99,102,241,0.1); border-radius: 12px; margin: 20px 0;">
                    {otp}
                </div>
                <p style="text-align: center; font-size: 13px; color: #64748b;">This code expires in 5 minutes.</p>
            </div>
        </body>
        </html>
        """
        msg.attach(MIMEText(body, "html"))

        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(SMTP_EMAIL, SMTP_PASSWORD)
        server.send_message(msg)
        server.quit()
        print(f"[OTP] Email sent to {to_email}")
        return True
    except Exception as e:
        print(f"[OTP] Email failed: {e}. OTP for {to_email}: {otp}")
        return False
