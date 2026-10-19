from django.contrib import admin

from .models import Project


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ("title", "company", "status", "featured", "is_published", "order")
    list_editable = ("featured", "is_published", "order")
    list_filter = ("status", "featured", "is_published")
    search_fields = ("title", "company", "summary")
    prepopulated_fields = {"slug": ("title",)}
