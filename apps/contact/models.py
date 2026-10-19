from django.db import models


class ContactMessage(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=30, blank=True)
    subject = models.CharField(max_length=150, blank=True)
    message = models.TextField(max_length=5000)
    ip_hash = models.CharField(max_length=64, blank=True, help_text="Salted hash, never the raw IP.")
    user_agent = models.CharField(max_length=255, blank=True)
    is_read = models.BooleanField(default=False)
    email_sent = models.BooleanField(default=False, help_text="Notification delivered through Resend.")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.name} <{self.email}> – {self.subject or self.message[:40]}"
