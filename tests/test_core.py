import pytest
from django.urls import reverse

from apps.core.models import PageView

pytestmark = pytest.mark.django_db


def test_health_is_ok_without_database_check(api, django_assert_num_queries):
    with django_assert_num_queries(0):
        res = api.get(reverse("health"))
    assert res.status_code == 200
    assert res.json()["status"] == "ok"
    assert "database" not in res.json()
    assert "X-Response-Time-Ms" in res


def test_health_deep_checks_database(api):
    res = api.get(reverse("health"), {"deep": "1"})
    assert res.status_code == 200
    assert res.json()["database"] == "ok"


def test_api_root_lists_endpoints(api):
    res = api.get(reverse("api-root"))
    assert res.status_code == 200
    assert {"health", "contact", "projects", "guestbook", "stats", "auth_me"} <= res.json()["endpoints"].keys()


def test_stats_hit_records_hashed_visitor(api):
    res = api.post(reverse("stats-hit"), {"path": "/backend"}, REMOTE_ADDR="203.0.113.7")
    assert res.status_code == 202
    view = PageView.objects.get()
    assert view.path == "/backend"
    assert "203.0.113.7" not in view.visitor_hash and len(view.visitor_hash) == 64


def test_stats_hit_rejects_invalid_path(api):
    res = api.post(reverse("stats-hit"), {"path": "javascript:alert(1)"})
    assert res.status_code == 400


def test_stats_are_cached(api):
    api.post(reverse("stats-hit"), {"path": "/"})
    first = api.get(reverse("stats"))
    assert first.status_code == 200
    assert first.json()["cached"] is False and first["X-Cache"] == "MISS"
    assert first.json()["total_views"] == 1
    assert len(first.json()["last_7_days"]) == 7

    api.post(reverse("stats-hit"), {"path": "/"})
    second = api.get(reverse("stats"))
    assert second.json()["cached"] is True and second["X-Cache"] == "HIT"
    assert second.json()["total_views"] == 1  # served from cache until the TTL expires


def test_unique_visitors_counts_distinct_hashes(api):
    api.post(reverse("stats-hit"), {"path": "/"}, REMOTE_ADDR="198.51.100.1")
    api.post(reverse("stats-hit"), {"path": "/backend"}, REMOTE_ADDR="198.51.100.1")
    api.post(reverse("stats-hit"), {"path": "/"}, REMOTE_ADDR="198.51.100.2")
    data = api.get(reverse("stats")).json()
    assert data["total_views"] == 3
    assert data["unique_visitors"] == 2
    assert data["top_paths"][0] == {"path": "/", "views": 2}


def test_openapi_schema_and_docs(api):
    assert api.get(reverse("schema")).status_code == 200
    assert api.get(reverse("swagger-ui")).status_code == 200
