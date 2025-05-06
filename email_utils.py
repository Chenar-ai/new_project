import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv
import os
from utils import create_access_token
from datetime import timedelta

load_dotenv()

EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:7090")

print("EMAIL_ADDRESS:", EMAIL_ADDRESS)
print("EMAIL_PASSWORD present:", bool(EMAIL_PASSWORD))


def send_verification_email(to_email: str, subject: str, body: str):
    subject = "Verify your email"
    token = create_access_token(
        data={"sub": to_email},
        roles=[],
        expires_delta=timedelta(hours=1)
    )

    print(f"Token created: {token}")  # Log the token

    verification_link = f"{FRONTEND_URL}/verify-email?token={token}"

    msg = MIMEMultipart()
    msg['From'] = EMAIL_ADDRESS
    msg['To'] = to_email
    msg['Subject'] = subject
    html_body = f"""
    <html>
      <body style="font-family: Arial, sans-serif; line-height: 1.6;">
        <div style="max-width: 600px; margin: auto; padding: 20px; border: 1px solid #eaeaea; border-radius: 8px;">
          <h2 style="color: #333;">Verify your email</h2>
          <p>Hi there,</p>
          <p>Thanks for signing up! Please verify your email address by clicking the button below:</p>
          <p style="text-align: center;">
            <a href="{verification_link}" style="background-color: #4CAF50; color: white; padding: 12px 20px; text-decoration: none; border-radius: 5px;">Verify Email</a>
          </p>
          <p>If you didn’t create an account, you can safely ignore this email.</p>
          <p style="color: #999; font-size: 12px;">This link will expire in 1 hour.</p>
        </div>
      </body>
    </html>
    """
    msg.attach(MIMEText(html_body, 'html'))

    # Debug print
    print("Attempting to send email...")
    print(f"From: {EMAIL_ADDRESS}")
    print(f"To: {to_email}")
    print(f"Frontend URL: {FRONTEND_URL}")
    print(f"Full Token: {token}")
    print(f"Password loaded: {'Yes' if EMAIL_PASSWORD else 'No'}")

    try:
        with smtplib.SMTP('smtp.gmail.com', 587, timeout=30) as server:
            server.starttls()
            server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            server.sendmail(EMAIL_ADDRESS, to_email, msg.as_string())
        print("✅ Email sent successfully.")
    except smtplib.SMTPAuthenticationError as e:
        print(f"❌ Authentication failed: {e.smtp_error.decode()}")
    except Exception as e:
        print(f"❌ Failed to send email: {e}")


def send_password_reset_email(to_email: str, subject: str, body: str):
    token = create_access_token(
        data={"sub": to_email},
        roles=[],  # You can add user roles here if needed
        expires_delta=timedelta(hours=1)
    )

    print(f"Password reset token created: {token}")  # Log the token

    reset_link = f"{FRONTEND_URL}/reset-password?token={token}"

    msg = MIMEMultipart()
    msg['From'] = EMAIL_ADDRESS
    msg['To'] = to_email
    msg['Subject'] = subject

    # Custom HTML for the password reset email
    html_body = f"""
    <html>
      <body style="font-family: Arial, sans-serif; line-height: 1.6;">
        <div style="max-width: 600px; margin: auto; padding: 20px; border: 1px solid #eaeaea; border-radius: 8px;">
          <h2 style="color: #333;">Reset your password</h2>
          <p>Hi there,</p>
          <p>We received a request to reset your password. Click the link below to create a new password:</p>
          <p style="text-align: center;">
            <a href="{reset_link}" style="background-color: #FF5722; color: white; padding: 12px 20px; text-decoration: none; border-radius: 5px;">Reset Password</a>
          </p>
          <p>If you didn’t request a password reset, you can safely ignore this email.</p>
          <p style="color: #999; font-size: 12px;">This link will expire in 1 hour.</p>
        </div>
      </body>
    </html>
    """
    msg.attach(MIMEText(html_body, 'html'))

    # Debug print
    print("Attempting to send password reset email...")
    print(f"From: {EMAIL_ADDRESS}")
    print(f"To: {to_email}")
    print(f"Frontend URL: {FRONTEND_URL}")
    print(f"Password reset link: {reset_link}")
    print(f"Password loaded: {'Yes' if EMAIL_PASSWORD else 'No'}")

    try:
        with smtplib.SMTP('smtp.gmail.com', 587, timeout=30) as server:
            server.starttls()
            server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            server.sendmail(EMAIL_ADDRESS, to_email, msg.as_string())
        print("✅ Password reset email sent successfully.")
    except smtplib.SMTPAuthenticationError as e:
        print(f"❌ Authentication failed: {e.smtp_error.decode()}")
    except Exception as e:
        print(f"❌ Failed to send email: {e}")
