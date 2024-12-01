import os
import logging
from celery import Celery
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import smtplib

celery_app = Celery('notification_tasks', broker='pyamqp://guest@rabbitmq//')

# Logger setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("notification_tasks")

def send_email(recipient, subject, message):
    """
    Sends an email using a secure SMTP connection.
    """
    smtp_server = "smtp.gmail.com"
    smtp_port = 587
    smtp_user = os.getenv("SMTP_USER")
    smtp_password = os.getenv("SMTP_PASSWORD")

    if not smtp_user or not smtp_password:
        logger.error("SMTP credentials are not set")
        raise Exception("SMTP credentials are not set")

    try:
        # Create a MIME email
        email = MIMEMultipart()
        email["From"] = smtp_user
        email["To"] = recipient
        email["Subject"] = subject
        email.attach(MIMEText(message, "plain"))

        # Connect and send email
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()  # Secure the connection
            server.login(smtp_user, smtp_password)  # Login to SMTP
            server.sendmail(smtp_user, recipient, email.as_string())

        logger.info(f"Email sent to {recipient}")
    except Exception as e:
        logger.error(f"Failed to send email to {recipient}: {e}")
        raise

@celery_app.task(name="tasks.process_notification")
def process_notification(notification_data):
    """
    Process a notification from the Celery queue.
    """
    try:
        # Use the notification_data directly
        notification = notification_data

        channel = notification.get("channel")
        recipient = notification.get("recipient")
        subject = notification.get("subject")
        message = notification.get("message")

        if channel == "email":
            send_email(recipient, subject, message)
        else:
            logger.warning(f"Unsupported notification channel: {channel}")
            raise ValueError(f"Unsupported channel: {channel}")
    except Exception as e:
        logger.error(f"Error processing notification: {e}")
        raise