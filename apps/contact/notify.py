"""E-mail notification for new contact messages via the Resend HTTP API.

Render's free tier blocks outbound SMTP ports (25/465/587), so an HTTP e-mail API is used instead.
Sending happens in a background thread after the DB commit: the visitor never waits for it,
and a failure never breaks the contact form (the message is already saved and visible in the admin).
"""
import logging
import threading
from html import escape

import requests
from django.conf import settings

logger = logging.getLogger(__name__)

RESEND_URL = "https://api.resend.com/emails"


def send_contact_notification(message_id: int) -> bool:
    from .models import ContactMessage

    if not (settings.RESEND_API_KEY and settings.CONTACT_NOTIFY_EMAIL):
        return False
    msg = ContactMessage.objects.filter(pk=message_id).first()
    if msg is None:
        return False

    rows = [("Name", msg.name), ("Email", msg.email), ("Phone", msg.phone or "–"), ("Subject", msg.subject or "–")]
    html = (
        "<h2>New message from your portfolio</h2><table>"
        + "".join(f"<tr><td><b>{k}</b></td><td>{escape(v)}</td></tr>" for k, v in rows)
        + f"</table><p style='white-space:pre-wrap'>{escape(msg.message)}</p>"
    )
    text = "\n".join(f"{k}: {v}" for k, v in rows) + f"\n\n{msg.message}"
    try:
        resp = requests.post(
            RESEND_URL,
            headers={
                "Authorization": f"Bearer {settings.RESEND_API_KEY}",
                "Idempotency-Key": f"contact-{msg.pk}",
            },
            json={
                "from": settings.RESEND_FROM,
                "to": [settings.CONTACT_NOTIFY_EMAIL],
                "reply_to": msg.email,
                "subject": f"Portfolio contact: {msg.subject or msg.name}"[:200],
                "html": html,
                "text": text,
            },
            timeout=10,
        )
        resp.raise_for_status()
    except requests.RequestException:
        logger.exception("Resend notification failed for contact message %s", msg.pk)
        return False
    ContactMessage.objects.filter(pk=msg.pk).update(email_sent=True)
    return True


def notify_in_background(message_id: int) -> None:
    threading.Thread(target=send_contact_notification, args=(message_id,), daemon=True).start()
