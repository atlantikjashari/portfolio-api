from django.conf import settings
from rest_framework import generics, status
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.throttling import AnonRateThrottle

from apps.core.throttling import AcceptedOnlyScopedThrottle, record_accepted
from apps.core.utils import anonymous_hash, client_ip

from .models import GuestbookEntry
from .serializers import GuestbookEntrySerializer


class GuestbookPagination(PageNumberPagination):
    page_size = 5
    page_size_query_param = "page_size"
    max_page_size = 20


class GuestbookListCreateView(generics.ListCreateAPIView):
    """GET: approved entries, newest first, paginated. POST: leave a message (throttled, honeypot, auto-moderated)."""

    serializer_class = GuestbookEntrySerializer
    pagination_class = GuestbookPagination
    queryset = GuestbookEntry.objects.filter(is_approved=True)
    throttle_classes = [AnonRateThrottle, AcceptedOnlyScopedThrottle]

    def get_throttles(self):
        # Only writes use the strict "guestbook" scope (accepted posts only); reads use the global anon rate.
        self.throttle_scope = "guestbook" if self.request.method == "POST" else None
        self._active_throttles = super().get_throttles()
        return self._active_throttles

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        record_accepted(self)
        if serializer.is_spam():
            return Response(
                {"detail": "Thanks for signing the guestbook!", "status": "published"},
                status=status.HTTP_201_CREATED,
            )
        reason = serializer.moderation_reason(serializer.validated_data["message"])
        entry = serializer.save(
            is_approved=settings.GUESTBOOK_AUTO_APPROVE and not reason,
            flagged_reason=reason,
            ip_hash=anonymous_hash(client_ip(request)),
        )
        detail = (
            "Thanks for signing the guestbook!"
            if entry.is_approved
            else "Thanks! Your message will appear after moderation."
        )
        return Response({"detail": detail, **serializer.data}, status=status.HTTP_201_CREATED)
