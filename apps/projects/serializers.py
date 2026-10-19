from rest_framework import serializers

from .models import Project


class ProjectSerializer(serializers.ModelSerializer):
    status_label = serializers.CharField(source="get_status_display", read_only=True)

    class Meta:
        model = Project
        fields = [
            "id",
            "slug",
            "title",
            "company",
            "role",
            "period",
            "summary",
            "description",
            "highlights",
            "tech",
            "status",
            "status_label",
            "live_url",
            "repo_url",
            "image_url",
            "featured",
            "order",
        ]
