from django.contrib import admin

from .models import PageView


@admin.register(PageView)
class PageViewAdmin(admin.ModelAdmin):
    list_display = ("path", "created_at", "visitor_hash")
    list_filter = ("path",)
    date_hierarchy = "created_at"
    readonly_fields = ("path", "visitor_hash", "created_at")
