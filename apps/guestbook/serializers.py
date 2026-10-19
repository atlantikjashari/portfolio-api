import re

from rest_framework import serializers

from .models import GuestbookEntry

LINK_RE = re.compile(r"(https?://|www\.|\b[a-z0-9-]+\.(com|net|org|ru|xyz|info|top)\b)", re.IGNORECASE)


class GuestbookEntrySerializer(serializers.ModelSerializer):
    website = serializers.CharField(required=False, allow_blank=True, write_only=True, max_length=200)
    status = serializers.SerializerMethodField()

    class Meta:
        model = GuestbookEntry
        fields = ["id", "name", "message", "created_at", "website", "status"]
        read_only_fields = ["id", "created_at", "status"]

    def get_status(self, obj) -> str:
        return "published" if obj.is_approved else "pending_moderation"

    def validate_name(self, value):
        value = " ".join(value.split())
        if len(value) < 2:
            raise serializers.ValidationError("Name must be at least 2 characters.")
        return value

    def validate_message(self, value):
        value = value.strip()
        if len(value) < 3:
            raise serializers.ValidationError("Message must be at least 3 characters.")
        return value

    def is_spam(self) -> bool:
        return bool(self.initial_data.get("website"))

    @staticmethod
    def moderation_reason(message: str) -> str:
        """Simple auto-moderation: links are the #1 spam signal, so they wait for manual approval."""
        if LINK_RE.search(message):
            return "Contains a link"
        if len(set(message)) <= 3 and len(message) > 10:
            return "Repeated characters"
        return ""

    def create(self, validated_data):
        validated_data.pop("website", None)
        return super().create(validated_data)
