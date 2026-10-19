from django.urls import path

from .views import ProjectDetailView, ProjectListView

urlpatterns = [
    path("", ProjectListView.as_view(), name="project-list"),
    path("<slug:slug>/", ProjectDetailView.as_view(), name="project-detail"),
]
