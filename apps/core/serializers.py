import re

from rest_framework import serializers

PATH_RE = re.compile(r"^/[A-Za-z0-9/_\-#.]*$")


class PageHitSerializer(serializers.Serializer):
    path = serializers.CharField(max_length=200, default="/")

    def validate_path(self, value):
        value = value.split("?")[0] or "/"
        if not PATH_RE.match(value):
            raise serializers.ValidationError("Must be a site path like '/' or '/backend'.")
        return value


class DailyCountSerializer(serializers.Serializer):
    date = serializers.DateField()
    views = serializers.IntegerField()


class PathCountSerializer(serializers.Serializer):
    path = serializers.CharField()
    views = serializers.IntegerField()


class StatsSerializer(serializers.Serializer):
    total_views = serializers.IntegerField()
    unique_visitors = serializers.IntegerField()
    views_today = serializers.IntegerField()
    last_7_days = DailyCountSerializer(many=True)
    top_paths = PathCountSerializer(many=True)
    generated_at = serializers.DateTimeField()
    cache_ttl_seconds = serializers.IntegerField()
    cached = serializers.BooleanField()


class HealthSerializer(serializers.Serializer):
    status = serializers.CharField()
    time = serializers.DateTimeField()
    uptime_seconds = serializers.IntegerField()
    version = serializers.CharField()
    database = serializers.CharField(required=False)
