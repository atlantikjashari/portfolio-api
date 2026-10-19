import pytest
from django.urls import reverse

from apps.projects.models import Project

pytestmark = pytest.mark.django_db


def test_seeded_projects_are_listed_in_order(api):
    res = api.get(reverse("project-list"))
    assert res.status_code == 200
    data = res.json()
    assert len(data) >= 6
    assert [p["order"] for p in data] == sorted(p["order"] for p in data)
    assert {"pabau-clinic-crm", "learniverse", "eventkickoff", "mybranda"} <= {p["slug"] for p in data}


def test_unpublished_projects_are_hidden(api):
    Project.objects.filter(slug="mybranda").update(is_published=False)
    slugs = {p["slug"] for p in api.get(reverse("project-list")).json()}
    assert "mybranda" not in slugs
    assert api.get(reverse("project-detail", args=["mybranda"])).status_code == 404


def test_featured_filter(api):
    data = api.get(reverse("project-list"), {"featured": "true"}).json()
    assert data and all(p["featured"] for p in data)


def test_project_detail_has_status_label(api):
    res = api.get(reverse("project-detail", args=["mybranda"]))
    assert res.status_code == 200
    assert res.json()["status"] == "offline"
    assert res.json()["status_label"] == "No longer online"
