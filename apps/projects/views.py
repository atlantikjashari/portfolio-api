from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import generics

from .models import Project
from .serializers import ProjectSerializer


@extend_schema(parameters=[OpenApiParameter("featured", bool, description="Only featured projects.")])
class ProjectListView(generics.ListAPIView):
    """Published projects, managed in the Django admin. Not paginated (small, fixed-size list)."""

    serializer_class = ProjectSerializer
    pagination_class = None

    def get_queryset(self):
        qs = Project.objects.filter(is_published=True)
        if self.request.query_params.get("featured") in ("1", "true"):
            qs = qs.filter(featured=True)
        return qs


class ProjectDetailView(generics.RetrieveAPIView):
    serializer_class = ProjectSerializer
    lookup_field = "slug"
    queryset = Project.objects.filter(is_published=True)
