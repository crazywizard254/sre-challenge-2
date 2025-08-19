import os
from celery import Celery
from email.message import EmailMessage
import smtplib

broker = os.getenv('CELERY_BROKER_URL', 'amqp://guest:guest@rabbitmq:5672//')
celery_app = Celery('tasks', broker=broker)


@celery_app.task(bind=True, name='tasks.send_validation_email')
def send_validation_email(self, to_address: str, part_id: int, title: str, token: str):
    # Send a simple validation email via SMTP to MailHog
    smtp_host = os.getenv('SMTP_HOST', 'mailhog')
    smtp_port = int(os.getenv('SMTP_PORT', 1025))
    base = os.getenv('BASE_URL', 'http://localhost:8080')
    msg = EmailMessage()
    msg['Subject'] = f'Validation for your listing: {title}'
    msg['From'] = os.getenv('SMTP_FROM', 'noreply@eea.com')
    msg['To'] = to_address
    link = f"{base}/validate/{token}"
    msg.set_content(f"Thank you. Your listing (id={part_id}, title={title}) was received.\n\nPlease validate your listing by visiting: {link}\n")
    try:
        with smtplib.SMTP(smtp_host, smtp_port, timeout=10) as s:
            s.send_message(msg)
        return {'status': 'sent'}
    except Exception as e:
        # Retry or fail
        raise self.retry(exc=e, countdown=10, max_retries=3)
