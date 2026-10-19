"""Idempotent post-deploy setup, run from build.sh (Render's free tier has no shell).

- creates/updates the public demo user used by the JWT auth demo (no staff rights)
- creates the admin superuser from DJANGO_SUPERUSER_* env vars if it doesn't exist yet
"""
import os

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Create the demo user and (optionally) the admin superuser from environment variables."

    def handle(self, *args, **options):
        User = get_user_model()

        demo, created = User.objects.get_or_create(username=settings.DEMO_USERNAME)
        demo.is_staff = demo.is_superuser = False
        demo.set_password(settings.DEMO_PASSWORD)
        demo.save()
        self.stdout.write(f"Demo user '{demo.username}' {'created' if created else 'updated'}.")

        username = os.environ.get("DJANGO_SUPERUSER_USERNAME")
        password = os.environ.get("DJANGO_SUPERUSER_PASSWORD")
        email = os.environ.get("DJANGO_SUPERUSER_EMAIL", "")
        if not (username and password):
            self.stdout.write("DJANGO_SUPERUSER_USERNAME/PASSWORD not set – skipping superuser.")
            return
        if username == settings.DEMO_USERNAME:
            self.stderr.write("Superuser must not use the demo username – skipping.")
            return
        if User.objects.filter(username=username).exists():
            self.stdout.write(f"Superuser '{username}' already exists.")
            return
        User.objects.create_superuser(username=username, email=email, password=password)
        self.stdout.write(self.style.SUCCESS(f"Superuser '{username}' created."))
