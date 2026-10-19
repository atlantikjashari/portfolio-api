from django.db import models


class GuestbookEntry(models.Model):
    name = models.CharField(max_length=40)
    message = models.CharField(max_length=280)
    is_approved = models.BooleanField(default=True, help_text="Only approved entries are public.")
    flagged_reason = models.CharField(max_length=120, blank=True, help_text="Why auto-moderation held it back.")
    ip_hash = models.CharField(max_length=64, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name_plural = "guestbook entries"

    def __str__(self):
        return f"{self.name}: {self.message[:40]}"
