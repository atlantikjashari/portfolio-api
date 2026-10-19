from django.urls import path

from .views import GuestbookListCreateView

urlpatterns = [
    path("", GuestbookListCreateView.as_view(), name="guestbook-list"),
]
