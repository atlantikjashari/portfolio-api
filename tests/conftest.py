import pytest
from django.core.cache import cache
from rest_framework.test import APIClient


@pytest.fixture(autouse=True)
def _test_settings(settings):
    settings.CACHES = {"default": {"BACKEND": "django.core.cache.backends.locmem.LocMemCache"}}
    settings.STORAGES = {
        **settings.STORAGES,
        "staticfiles": {"BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"},
    }
    settings.SECURE_SSL_REDIRECT = False
    settings.RESEND_API_KEY = ""
    cache.clear()  # throttling + stats cache state must not leak between tests
    yield
    cache.clear()


@pytest.fixture
def api():
    return APIClient()
