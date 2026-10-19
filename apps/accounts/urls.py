from django.urls import path

from .views import MeView, ThrottledTokenObtainPairView, ThrottledTokenRefreshView

urlpatterns = [
    path("token/", ThrottledTokenObtainPairView.as_view(), name="token-obtain"),
    path("token/refresh/", ThrottledTokenRefreshView.as_view(), name="token-refresh"),
    path("me/", MeView.as_view(), name="auth-me"),
]
