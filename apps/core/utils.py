import hashlib

from django.conf import settings
from django.utils import timezone
from rest_framework.throttling import BaseThrottle


def client_ip(request) -> str:
    """Client IP resolved the same way DRF throttling does (respects NUM_PROXIES)."""
    return BaseThrottle().get_ident(request)


def anonymous_hash(*parts: str) -> str:
    """Salted SHA-256 so no raw IP address is ever stored."""
    raw = "|".join([settings.SECRET_KEY, *parts])
    return hashlib.sha256(raw.encode()).hexdigest()


def daily_visitor_hash(request) -> str:
    """Same visitor on the same day -> same hash; rotates daily (privacy-friendly unique count)."""
    ua = request.META.get("HTTP_USER_AGENT", "")[:200]
    return anonymous_hash(client_ip(request), ua, timezone.localdate().isoformat())
