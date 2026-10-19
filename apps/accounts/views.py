from datetime import datetime

from django.conf import settings
from django.utils import timezone
from drf_spectacular.utils import extend_schema, inline_serializer
from rest_framework import serializers
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView


class ThrottledTokenObtainPairView(TokenObtainPairView):
    """POST username + password -> access (10 min) and refresh (12 h) JWTs."""

    throttle_scope = "auth"


class ThrottledTokenRefreshView(TokenRefreshView):
    throttle_scope = "auth"


class MeView(APIView):
    """Protected endpoint: only works with a valid `Authorization: Bearer <access token>` header."""

    permission_classes = [IsAuthenticated]

    @extend_schema(
        responses=inline_serializer(
            "Me",
            {
                "username": serializers.CharField(),
                "is_demo": serializers.BooleanField(),
                "token_expires_at": serializers.DateTimeField(),
                "message": serializers.CharField(),
                "server_time": serializers.DateTimeField(),
            },
        )
    )
    def get(self, request):
        exp = request.auth.get("exp") if request.auth is not None else None
        return Response(
            {
                "username": request.user.get_username(),
                "is_demo": request.user.get_username() == settings.DEMO_USERNAME,
                "token_expires_at": datetime.fromtimestamp(exp, tz=timezone.get_current_timezone())
                if exp
                else None,
                "message": "🔓 You reached a protected endpoint. Your JWT was verified by the server.",
                "server_time": timezone.localtime(),
            }
        )
