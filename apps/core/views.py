import time
from datetime import timedelta

from django.conf import settings
from django.core.cache import cache
from django.db import connection
from django.db.models import Count, Q
from django.db.models.functions import TruncDate
from django.utils import timezone
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework.views import APIView

from .models import PageView
from .serializers import HealthSerializer, PageHitSerializer, StatsSerializer
from .utils import daily_visitor_hash

STARTED_AT = time.monotonic()
STATS_CACHE_KEY = "stats:v1"


@extend_schema(exclude=True)
@api_view(["GET"])
@permission_classes([AllowAny])
def api_root(request):
    """Index of the public endpoints (used by the Backend Lab API explorer)."""
    return Response(
        {
            "name": "Atlantik Jashari – Portfolio API",
            "docs": reverse("swagger-ui", request=request),
            "schema": reverse("schema", request=request),
            "endpoints": {
                "health": reverse("health", request=request),
                "contact": reverse("contact-create", request=request),
                "projects": reverse("project-list", request=request),
                "guestbook": reverse("guestbook-list", request=request),
                "stats": reverse("stats", request=request),
                "stats_hit": reverse("stats-hit", request=request),
                "auth_token": reverse("token-obtain", request=request),
                "auth_refresh": reverse("token-refresh", request=request),
                "auth_me": reverse("auth-me", request=request),
            },
        }
    )


class HealthView(APIView):
    """Liveness check. Skips the database unless ?deep=1, so pinging it never wakes Neon."""

    authentication_classes = []
    throttle_classes = []

    @extend_schema(
        responses=HealthSerializer,
        parameters=[OpenApiParameter("deep", bool, description="Also check the database connection.")],
    )
    def get(self, request):
        data = {
            "status": "ok",
            "time": timezone.now(),
            "uptime_seconds": int(time.monotonic() - STARTED_AT),
            "version": settings.APP_VERSION,
        }
        code = status.HTTP_200_OK
        if request.query_params.get("deep") in ("1", "true"):
            try:
                with connection.cursor() as cursor:
                    cursor.execute("SELECT 1")
                data["database"] = "ok"
            except Exception:  # noqa: BLE001 - report the failure instead of crashing
                data["database"] = "unavailable"
                data["status"] = "degraded"
                code = status.HTTP_503_SERVICE_UNAVAILABLE
        return Response(HealthSerializer(data).data, status=code)


def compute_stats() -> dict:
    today = timezone.localdate()
    week_start = today - timedelta(days=6)
    qs = PageView.objects.all()
    per_day = {
        row["day"]: row["views"]
        for row in qs.filter(created_at__date__gte=week_start)
        .annotate(day=TruncDate("created_at"))
        .values("day")
        .annotate(views=Count("id"))
        .order_by()
    }
    # one aggregate query, so the totals are consistent with each other even while new hits arrive
    totals = qs.aggregate(
        total=Count("id"),
        unique=Count("visitor_hash", distinct=True),
        today=Count("id", filter=Q(created_at__date=today)),
    )
    return {
        "total_views": totals["total"],
        "unique_visitors": totals["unique"],
        "views_today": totals["today"],
        "last_7_days": [
            {"date": week_start + timedelta(days=i), "views": per_day.get(week_start + timedelta(days=i), 0)}
            for i in range(7)
        ],
        "top_paths": list(qs.order_by().values("path").annotate(views=Count("id")).order_by("-views", "path")[:5]),
        "generated_at": timezone.now(),
    }


class StatsView(APIView):
    """Aggregated page-view analytics, cached for STATS_CACHE_SECONDS (database cache, no Redis needed)."""

    @extend_schema(responses=StatsSerializer)
    def get(self, request):
        ttl = settings.STATS_CACHE_SECONDS
        payload = cache.get(STATS_CACHE_KEY)
        cached = payload is not None
        if not cached:
            payload = compute_stats()
            cache.set(STATS_CACHE_KEY, payload, ttl)
        data = StatsSerializer({**payload, "cache_ttl_seconds": ttl, "cached": cached}).data
        response = Response(data)
        response["X-Cache"] = "HIT" if cached else "MISS"
        return response


class StatsHitView(APIView):
    """Records one page view. Visitors are identified by a daily-rotating salted hash, never by raw IP."""

    throttle_scope = "stats"

    @extend_schema(request=PageHitSerializer, responses={202: PageHitSerializer})
    def post(self, request):
        serializer = PageHitSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        PageView.objects.create(path=serializer.validated_data["path"], visitor_hash=daily_visitor_hash(request))
        return Response({"recorded": True, **serializer.data}, status=status.HTTP_202_ACCEPTED)
