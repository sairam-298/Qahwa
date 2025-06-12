import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from dotenv import load_dotenv

load_dotenv()

EMAIL_HOST = os.getenv("EMAIL_HOST")
EMAIL_PORT = int(os.getenv("EMAIL_PORT", 587))
EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")

def send_confirmation_email(name, recipient, date, time, booking_id):
    subject = "☕ Qahwa Workshop Booking Confirmation"

    html_body = f"""
    <div style="font-family: Arial, sans-serif; color: #5C4033;">
        <p>Hello {name},</p>

        <p>Thank you for your booking @ the <strong>Coffee Brewing & Preparation Workshop</strong> at <strong>Qahwa Café</strong>.</p>

        <p>
            📅 <strong>Date:</strong> {date}<br>
            ⏰ <strong>Time:</strong> {time}<br>
            🆔 <strong>Booking ID:</strong> {booking_id}<br>
            📍 <strong>Location:</strong> The Majlis (our café's backroom)<br>
            💰 <strong>Cost:</strong> ₹800 per participant.
        </p>

        <p>Please keep this ID for future reference.</p>

        <p>Thank you for choosing Qahwa ☕!<br>
        We're excited to have you with us! Reach out if you have any questions.</p>

        <p> ~ Team Qahwa</p>
    </div>
    """

    msg = MIMEMultipart("alternative")
    msg["From"] = EMAIL_ADDRESS
    msg["To"] = recipient
    msg["Subject"] = subject

    msg.attach(MIMEText(html_body, "html"))

    try:
        with smtplib.SMTP(EMAIL_HOST, EMAIL_PORT) as server:
            server.starttls()
            server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            server.send_message(msg)
        print(f"✅ Email sent to {recipient} at {time}")
        return True
    except Exception as e:
        print(f"❌ Failed to send email: {e}")
        return False
