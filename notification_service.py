from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, EmailStr
from tasks import process_notification
import pika
import logging
import json

# Initialize FastAPI app
app = FastAPI(title="Notification Engine", version="1.0")

# Configure RabbitMQ connection
RABBITMQ_HOST = "rabbitmq"
QUEUE_NAME = "notification_queue"

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("notification_engine")

# Notification request model
class NotificationRequest(BaseModel):
    channel: str  # e.g., "email"
    recipient: EmailStr
    subject: str
    message: str

def publish_to_queue(notification_data: dict):
    """
    Publishes a message to the RabbitMQ queue.
    """
    try:
        connection = pika.BlockingConnection(pika.ConnectionParameters(host=RABBITMQ_HOST))
        channel = connection.channel()

        channel.queue_declare(queue=QUEUE_NAME, durable=True)

        channel.basic_publish(
            exchange="",
            routing_key=QUEUE_NAME,
            body=json.dumps(notification_data),
            properties=pika.BasicProperties(delivery_mode=2),  # Make message persistent
        )
        logger.info(f"Message published to queue: {notification_data}")
        connection.close()
    except Exception as e:
        logger.error(f"Failed to publish message: {e}")
        raise HTTPException(status_code=500, detail="Failed to publish notification")

@app.post("/send-notification/")
async def send_notification(request: NotificationRequest):
    """
    API endpoint to accept and publish notifications.
    """
    try:
        publish_to_queue(request.dict())
        process_notification.delay(request.dict())
        return {"status": "queued", "notification": request.dict()}
    except Exception as e:
        logger.error(f"Error queuing notification: {e}")
        raise HTTPException(status_code=500, detail="Failed to queue notification")
