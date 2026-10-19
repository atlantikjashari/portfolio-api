from django.contrib import admin

from .models import GuestbookEntry


@admin.register(GuestbookEntry)
class GuestbookEntryAdmin(admin.ModelAdmin):
    list_display = ("name", "message", "is_approved", "flagged_reason", "created_at")
    list_filter = ("is_approved", "created_at")
    list_editable = ("is_approved",)
    search_fields = ("name", "message")
    readonly_fields = ("ip_hash", "created_at")
    actions = ["approve", "hide"]

    @admin.action(description="Approve (make public)")
    def approve(self, request, queryset):
        queryset.update(is_approved=True, flagged_reason="")

    @admin.action(description="Hide from the public guestbook")
    def hide(self, request, queryset):
        queryset.update(is_approved=False)
