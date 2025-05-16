import os
from dotenv import load_dotenv
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.date import DateTrigger
import pytz
from email_utils import send_email_smtp  # Use the email utility function to send the email
from datetime import datetime
from models import Booking, User, Service  # Assuming these are your model classes
from database import SessionLocal

load_dotenv()

# Get the FRONTEND_URL from the environment variables
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:7010")  # Default to localhost if not found

# Initialize the scheduler
scheduler = BackgroundScheduler()

def send_reminder_email_job(customer_email: str, subject: str, booking_details: dict):
    # Ensure keys exist before accessing
    customer_name = booking_details.get('user_full_name', 'Customer')
    provider_name = booking_details.get('provider_full_name', 'Provider')
    service_name = booking_details.get('service_name', 'Service')
    booking_date = booking_details.get('booking_date', 'Date not available')
    reminder_link = f"{FRONTEND_URL}/view-booking/{booking_details.get('id', '')}"

    # Create the HTML body for the email
    html_body = f"""
    <html>
      <body style="font-family: Arial, sans-serif; line-height: 1.6;">
        <div style="max-width: 600px; margin: auto; padding: 20px; border: 1px solid #eaeaea; border-radius: 8px;">
          <h2 style="color: #333;">Reminder: Upcoming Booking</h2>
          <p>Hi {customer_name},</p>
          <p>This is a friendly reminder about your upcoming booking for the service:</p>

          <div style="margin-top: 20px; padding: 10px; background-color: #f9f9f9; border-radius: 5px;">
            <p><strong>Service Provider:</strong> {provider_name}</p>
            <p><strong>Service:</strong> {service_name}</p>
            <p><strong>Booking Date:</strong> {booking_date}</p>
          </div>

          <p>Please make sure to be on time. You can review or cancel the booking by clicking the link below:</p>
          <p style="text-align: center;">
            <a href="{reminder_link}" style="background-color: #FF5722; color: white; padding: 12px 20px; text-decoration: none; border-radius: 5px;">View Your Booking</a>
          </p>

          <p>Thank you for choosing our services! We look forward to serving you.</p>
          <p style="color: #999; font-size: 12px;">This link will expire 1 hour before your booking time.</p>
        </div>
      </body>
    </html>
    """

    send_email_smtp(customer_email, subject, html_body)

def schedule_reminder_email(booking_details: dict, reminder_time: datetime):
    db = SessionLocal()  # Get a new session for the background task

    try:
        # Access data from the dictionary
        user_id = booking_details['user_id']
        provider_id = booking_details['provider_id']
        service_id = booking_details['service_id']

        # Reload related data (user, provider, service)
        user = db.query(User).filter(User.id == user_id).first()
        provider = db.query(User).filter(User.id == provider_id).first()
        service = db.query(Service).filter(Service.id == service_id).first()

        # Access the customer name, provider name, and service name
        customer_name = user.full_name
        provider_name = provider.full_name
        service_name = service.name

        # Prepare the email details
        reminder_link = f"{FRONTEND_URL}/view-booking/{booking_details['id']}"

        booking_details_dict = {
            "user_full_name": customer_name,
            "provider_full_name": provider_name,
            "service_name": service_name,
            "booking_date": booking_details['booking_date'],
            "id": booking_details['id'],
        }

        # Schedule the email job at the reminder time
        scheduler.add_job(
            send_reminder_email_job,
            DateTrigger(run_date=reminder_time, timezone=pytz.timezone('Asia/Kuala_Lumpur')),
            args=[user.email, "Reminder: Your Upcoming Booking", booking_details_dict]
        )

    except Exception as e:
        print(f"Error scheduling reminder email: {e}")

    finally:
        # Ensure the session is closed after use
        db.close()


# Start the scheduler
def start_scheduler():
    scheduler.start()

# Gracefully shutdown the scheduler on app shutdown
def stop_scheduler():
    scheduler.shutdown()
