import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv
import os
from utils import create_access_token
from datetime import timedelta
from models import Booking

# Load environment variables
load_dotenv()

EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:7010")  # Default to localhost if not found

print("EMAIL_ADDRESS:", EMAIL_ADDRESS)
print("EMAIL_PASSWORD present:", bool(EMAIL_PASSWORD))


# Function to send email via SMTP
def send_email_smtp(to_email: str, subject: str, html_body: str):
    msg = MIMEMultipart()
    msg['From'] = EMAIL_ADDRESS
    msg['To'] = to_email
    msg['Subject'] = subject
    msg.attach(MIMEText(html_body, 'html'))  # Attach the HTML body content

    try:
        # Establish SMTP connection
        with smtplib.SMTP('smtp.gmail.com', 587, timeout=30) as server:
            server.starttls()  # Secure the connection
            server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            server.sendmail(EMAIL_ADDRESS, to_email, msg.as_string())
        print(f"✅ Email sent successfully to {to_email}.")
    except smtplib.SMTPAuthenticationError as e:
        print(f"❌ Authentication failed: {e.smtp_error.decode()}")
    except Exception as e:
        print(f"❌ Failed to send email: {e}")


# Function to send a booking confirmation email (confirm the booking)
def send_booking_confirmation_email(to_email: str, subject: str, booking_details: Booking):
    subject = "Booking Confirmation"

    # Access the customer_name (full_name of the associated user)
    customer_name = booking_details.user.full_name  # Access the user's full name via the 'user' relationship
    provider_name = booking_details.provider.full_name  # Similarly, get the provider_name
    service_name = booking_details.service.name  # Get the service name
    confirmation_link = f"{FRONTEND_URL}/view-booking/{booking_details.id}"  # Booking ID is accessed via dot notation

    html_body = f"""
    <html>
      <body style="font-family: Arial, sans-serif; line-height: 1.6;">
        <div style="max-width: 600px; margin: auto; padding: 20px; border: 1px solid #eaeaea; border-radius: 8px;">
          <h2 style="color: #333;">Your Booking is Confirmed!</h2>
          <p>Hi {customer_name},</p>
          <p>Your booking has been successfully confirmed for the following service:</p>

          <div style="margin-top: 20px; padding: 10px; background-color: #f9f9f9; border-radius: 5px;">
            <p><strong>Service Provider:</strong> {provider_name}</p>
            <p><strong>Service:</strong> {service_name}</p>
            <p><strong>Booking Date:</strong> {booking_details.booking_date}</p>
          </div>

          <p>You can review your booking details by clicking the link below:</p>
          <p style="text-align: center;">
            <a href="{confirmation_link}" style="background-color: #FF5722; color: white; padding: 12px 20px; text-decoration: none; border-radius: 5px;">View Your Booking</a>
          </p>

          <p>Thank you for choosing our services!</p>
        </div>
      </body>
    </html>
    """

    send_email_smtp(to_email, subject, html_body)


# Function to send a user verification email
def send_verification_email(to_email: str, subject: str, body: str):
    subject = "Verify your email"
    token = create_access_token(
        data={"sub": to_email},
        roles=[],  # You can add user roles here if needed
        expires_delta=timedelta(hours=1)
    )

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

    send_email_smtp(to_email, subject, html_body)


# Function to send a password reset email
def send_password_reset_email(to_email: str, subject: str, body: str):
    token = create_access_token(
        data={"sub": to_email},
        roles=[],  # You can add user roles here if needed
        expires_delta=timedelta(hours=1)
    )

    reset_link = f"{FRONTEND_URL}/reset-password?token={token}"

    msg = MIMEMultipart()
    msg['From'] = EMAIL_ADDRESS
    msg['To'] = to_email
    msg['Subject'] = subject

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

    send_email_smtp(to_email, subject, html_body)
