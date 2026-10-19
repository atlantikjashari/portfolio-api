from unittest import mock

import pytest
from django.urls import reverse

from apps.contact import notify
from apps.contact.models import ContactMessage

pytestmark = pytest.mark.django_db

VALID = {
    "name": "Jane Recruiter",
    "email": "jane@example.com",
    "phone": "+383 45 000 000",
    "subject": "Frontend role",
    "message": "Hi Atlantik, let's talk about a role on our team.",
}


def test_valid_message_is_saved(api):
    res = api.post(reverse("contact-create"), VALID)
    assert res.status_code == 201, res.json()
    msg = ContactMessage.objects.get()
    assert msg.email == "jane@example.com" and msg.phone == "+383 45 000 000"
    assert msg.ip_hash and "127.0.0.1" not in msg.ip_hash
    assert "website" not in res.json()


@pytest.mark.parametrize(
    "field,value",
    [("email", "not-an-email"), ("name", "J"), ("message", "too short"), ("phone", "call me maybe")],
)
def test_validation_errors(api, field, value):
    res = api.post(reverse("contact-create"), {**VALID, field: value})
    assert res.status_code == 400
    assert field in res.json()
    assert ContactMessage.objects.count() == 0


def test_honeypot_pretends_success_but_stores_nothing(api):
    res = api.post(reverse("contact-create"), {**VALID, "website": "http://spam.example"})
    assert res.status_code == 201
    assert ContactMessage.objects.count() == 0


def test_contact_is_rate_limited(api, settings):
    settings.REST_FRAMEWORK = {
        **settings.REST_FRAMEWORK,
        "DEFAULT_THROTTLE_RATES": {**settings.REST_FRAMEWORK["DEFAULT_THROTTLE_RATES"], "contact": "2/hour"},
    }
    from rest_framework.settings import api_settings
    from rest_framework.throttling import SimpleRateThrottle

    with mock.patch.object(SimpleRateThrottle, "THROTTLE_RATES", api_settings.DEFAULT_THROTTLE_RATES):
        codes = [api.post(reverse("contact-create"), VALID).status_code for _ in range(3)]
    assert codes == [201, 201, 429]


def test_invalid_requests_do_not_consume_quota(api, settings):
    from rest_framework.settings import api_settings
    from rest_framework.throttling import SimpleRateThrottle

    rates = {**settings.REST_FRAMEWORK["DEFAULT_THROTTLE_RATES"], "contact": "2/hour"}
    with mock.patch.object(SimpleRateThrottle, "THROTTLE_RATES", rates):
        invalid = [api.post(reverse("contact-create"), {**VALID, "email": "bad"}).status_code for _ in range(5)]
        valid = [api.post(reverse("contact-create"), VALID).status_code for _ in range(3)]
    assert invalid == [400] * 5
    assert valid == [201, 201, 429]
    assert ContactMessage.objects.count() == 2


def test_notification_sent_via_resend(settings):
    settings.RESEND_API_KEY = "re_test"
    settings.CONTACT_NOTIFY_EMAIL = "me@example.com"
    msg = ContactMessage.objects.create(name="Jane", email="jane@example.com", message="Hello there, Atlantik!")
    with mock.patch.object(notify.requests, "post") as post:
        post.return_value.raise_for_status.return_value = None
        assert notify.send_contact_notification(msg.pk) is True
    payload = post.call_args.kwargs["json"]
    assert payload["to"] == ["me@example.com"] and payload["reply_to"] == "jane@example.com"
    assert post.call_args.kwargs["headers"]["Authorization"] == "Bearer re_test"
    msg.refresh_from_db()
    assert msg.email_sent is True


def test_notification_failure_does_not_raise(settings):
    settings.RESEND_API_KEY = "re_test"
    settings.CONTACT_NOTIFY_EMAIL = "me@example.com"
    msg = ContactMessage.objects.create(name="Jane", email="jane@example.com", message="Hello there, Atlantik!")
    with mock.patch.object(notify.requests, "post", side_effect=notify.requests.ConnectionError):
        assert notify.send_contact_notification(msg.pk) is False
    msg.refresh_from_db()
    assert msg.email_sent is False


def test_notification_skipped_without_api_key():
    msg = ContactMessage.objects.create(name="Jane", email="jane@example.com", message="Hello there, Atlantik!")
    with mock.patch.object(notify.requests, "post") as post:
        assert notify.send_contact_notification(msg.pk) is False
    post.assert_not_called()
