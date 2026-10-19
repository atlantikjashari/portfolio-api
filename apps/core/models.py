from django.db import models


class PageView(models.Model):
    path = models.CharField(max_length=200, db_index=True)
    visitor_hash = models.CharField(max_length=64, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.path} @ {self.created_at:%Y-%m-%d %H:%M}"
