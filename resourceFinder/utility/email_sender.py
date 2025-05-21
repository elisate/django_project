from django.core.mail import EmailMessage
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

def send_email(to_email, subject, message, from_email=None):
    if from_email is None:
        from_email = settings.EMAIL_HOST_USER

    try:
        email = EmailMessage(
            subject=subject,
            body=message,
            from_email=from_email,
            to=[to_email] if isinstance(to_email, str) else to_email,
        )
        email.content_subtype = "html"
        result = email.send()
        logger.info(f"Email send result: {result}")
        return result
    except Exception as e:
        logger.error(f"Email sending failed: {e}")
        return 0
