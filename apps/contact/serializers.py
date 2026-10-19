import re

from rest_framework import serializers

from .models import ContactMessage

PHONE_RE = re.compile(r"^\+?[0-9 ()\-]{6,30}$")


class ContactMessageSerializer(serializers.ModelSerializer):
    # Honeypot: hidden in the UI, so only bots fill it in. Never stored.
    website = serializers.CharField(required=False, allow_blank=True, write_only=True, max_length=200)

    class Meta:
        model = ContactMessage
        fields = ["id", "name", "email", "phone", "subject", "message", "website", "created_at"]
        read_only_fields = ["id", "created_at"]
        extra_kwargs = {
            "phone": {"required": False},
            "subject": {"required": False},
        }

    def validate_name(self, value):
        value = value.strip()
        if len(value) < 2:
            raise serializers.ValidationError("Please enter your name (at least 2 characters).")
        return value

    def validate_phone(self, value):
        value = value.strip()
        if value and not PHONE_RE.match(value):
            raise serializers.ValidationError("Enter a valid phone number, e.g. +383 45 000 000.")
        return value

    def validate_message(self, value):
        value = value.strip()
        if len(value) < 10:
            raise serializers.ValidationError("Your message should be at least 10 characters long.")
        return value

    def is_spam(self) -> bool:
        return bool(self.initial_data.get("website"))

    def create(self, validated_data):
        validated_data.pop("website", None)
        return super().create(validated_data)
