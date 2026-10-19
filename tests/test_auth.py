import pytest
from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.urls import reverse

pytestmark = pytest.mark.django_db


@pytest.fixture
def demo_user(settings):
    call_command("bootstrap")
    return settings.DEMO_USERNAME, settings.DEMO_PASSWORD


def test_protected_endpoint_requires_token(api):
    assert api.get(reverse("auth-me")).status_code == 401


def test_login_and_access_protected_endpoint(api, demo_user):
    username, password = demo_user
    tokens = api.post(reverse("token-obtain"), {"username": username, "password": password})
    assert tokens.status_code == 200
    access = tokens.json()["access"]
    api.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")
    me = api.get(reverse("auth-me"))
    assert me.status_code == 200
    assert me.json()["username"] == username and me.json()["is_demo"] is True


def test_refresh_token(api, demo_user):
    username, password = demo_user
    refresh = api.post(reverse("token-obtain"), {"username": username, "password": password}).json()["refresh"]
    res = api.post(reverse("token-refresh"), {"refresh": refresh})
    assert res.status_code == 200 and "access" in res.json()


def test_wrong_password_and_bad_token(api, demo_user):
    username, _ = demo_user
    assert api.post(reverse("token-obtain"), {"username": username, "password": "nope"}).status_code == 401
    api.credentials(HTTP_AUTHORIZATION="Bearer not-a-real-token")
    assert api.get(reverse("auth-me")).status_code == 401


def test_demo_user_has_no_admin_rights(demo_user):
    user = get_user_model().objects.get(username=demo_user[0])
    assert not user.is_staff and not user.is_superuser


def test_bootstrap_creates_superuser_from_env(monkeypatch):
    monkeypatch.setenv("DJANGO_SUPERUSER_USERNAME", "atlantik")
    monkeypatch.setenv("DJANGO_SUPERUSER_PASSWORD", "a-strong-pass-123")
    call_command("bootstrap")
    call_command("bootstrap")  # idempotent
    user = get_user_model().objects.get(username="atlantik")
    assert user.is_superuser and user.check_password("a-strong-pass-123")
