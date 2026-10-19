from django.contrib import admin

from .models import ContactMessage


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "subject", "created_at", "is_read", "email_sent")
    list_filter = ("is_read", "email_sent", "created_at")
    search_fields = ("name", "email", "subject", "message")
    readonly_fields = ("name", "email", "phone", "subject", "message", "ip_hash", "user_agent", "email_sent", "created_at")
    actions = ["mark_read", "mark_unread"]

    @admin.action(description="Mark selected messages as read")
    def mark_read(self, request, queryset):
        queryset.update(is_read=True)

    @admin.action(description="Mark selected messages as unread")
    def mark_unread(self, request, queryset):
        queryset.update(is_read=False)
