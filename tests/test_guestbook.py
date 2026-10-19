import pytest
from django.urls import reverse

from apps.guestbook.models import GuestbookEntry

pytestmark = pytest.mark.django_db


def test_post_and_list_entry(api):
    res = api.post(reverse("guestbook-list"), {"name": "Ana", "message": "Great portfolio!"})
    assert res.status_code == 201
    assert res.json()["status"] == "published"
    listing = api.get(reverse("guestbook-list")).json()
    assert listing["count"] == 1
    assert listing["results"][0]["message"] == "Great portfolio!"


def test_pagination(api):
    GuestbookEntry.objects.bulk_create(GuestbookEntry(name=f"Visitor {i}", message="Hello!") for i in range(12))
    page1 = api.get(reverse("guestbook-list")).json()
    assert page1["count"] == 12 and len(page1["results"]) == 5 and page1["next"]
    page3 = api.get(reverse("guestbook-list"), {"page": 3}).json()
    assert len(page3["results"]) == 2 and page3["next"] is None


def test_links_are_held_for_moderation(api):
    res = api.post(reverse("guestbook-list"), {"name": "Bot", "message": "Buy now at https://spam.example"})
    assert res.status_code == 201
    assert res.json()["status"] == "pending_moderation"
    entry = GuestbookEntry.objects.get()
    assert entry.is_approved is False and entry.flagged_reason == "Contains a link"
    assert api.get(reverse("guestbook-list")).json()["count"] == 0


def test_manual_moderation_mode(api, settings):
    settings.GUESTBOOK_AUTO_APPROVE = False
    res = api.post(reverse("guestbook-list"), {"name": "Ana", "message": "Hello there"})
    assert res.json()["status"] == "pending_moderation"


@pytest.mark.parametrize("payload", [{"name": "A", "message": "Hello"}, {"name": "Ana", "message": "x" * 281}, {"name": "Ana"}])
def test_validation(api, payload):
    assert api.post(reverse("guestbook-list"), payload).status_code == 400


def test_honeypot(api):
    res = api.post(reverse("guestbook-list"), {"name": "Bot", "message": "hello", "website": "x"})
    assert res.status_code == 201
    assert GuestbookEntry.objects.count() == 0
