from django.db import models


class Project(models.Model):
    class Status(models.TextChoices):
        LIVE = "live", "Live"
        IN_DEVELOPMENT = "in_development", "In development"
        PRIVATE = "private", "Private / under NDA"
        OFFLINE = "offline", "No longer online"

    title = models.CharField(max_length=120)
    slug = models.SlugField(unique=True)
    company = models.CharField(max_length=120, blank=True)
    role = models.CharField(max_length=120, blank=True)
    period = models.CharField(max_length=60, blank=True, help_text="e.g. 'Apr 2024 – Apr 2025'")
    summary = models.CharField(max_length=300)
    description = models.TextField(blank=True)
    highlights = models.JSONField(default=list, blank=True, help_text="List of short bullet points.")
    tech = models.JSONField(default=list, blank=True, help_text='List of technologies, e.g. ["Vue", "Nuxt"].')
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.LIVE)
    live_url = models.URLField(blank=True)
    repo_url = models.URLField(blank=True)
    image_url = models.URLField(blank=True)
    featured = models.BooleanField(default=False)
    order = models.PositiveIntegerField(default=0, help_text="Lower numbers are shown first.")
    is_published = models.BooleanField(default=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["order", "title"]

    def __str__(self):
        return self.title
