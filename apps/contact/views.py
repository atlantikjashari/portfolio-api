import logging

from django.db import transaction
from drf_spectacular.utils import OpenApiExample, extend_schema
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.throttling import AnonRateThrottle

from apps.core.throttling import AcceptedOnlyScopedThrottle, record_accepted
from apps.core.utils import anonymous_hash, client_ip

from . import notify
from .serializers import ContactMessageSerializer

logger = logging.getLogger(__name__)


class ContactCreateView(generics.CreateAPIView):
    """Contact form endpoint: validated, rate limited (5/hour per IP) and protected by a honeypot field."""

    serializer_class = ContactMessageSerializer
    throttle_scope = "contact"
    # only accepted submissions count towards the 5/hour limit (validation errors don't burn quota)
    throttle_classes = [AnonRateThrottle, AcceptedOnlyScopedThrottle]

    def get_throttles(self):
        self._active_throttles = super().get_throttles()
        return self._active_throttles

    @extend_schema(
        examples=[
            OpenApiExample(
                "Valid message",
                value={
                    "name": "Jane Recruiter",
                    "email": "jane@example.com",
                    "subject": "Frontend role",
                    "message": "Hi Atlantik, I'd love to talk about a role on our team.",
                },
                request_only=True,
            )
        ]
    )
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        record_accepted(self)
        if serializer.is_spam():
            # Pretend it worked so bots learn nothing; nothing is stored or sent.
            logger.info("Contact honeypot triggered")
            return Response({"detail": "Thanks! Your message has been sent."}, status=status.HTTP_201_CREATED)
        message = serializer.save(
            ip_hash=anonymous_hash(client_ip(request)),
            user_agent=request.META.get("HTTP_USER_AGENT", "")[:255],
        )
        transaction.on_commit(lambda: notify.notify_in_background(message.pk))
        return Response(
            {"detail": "Thanks! Your message has been sent.", **serializer.data},
            status=status.HTTP_201_CREATED,
        )
