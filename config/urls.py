from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView

from apps.core.views import api_root

admin.site.site_header = "Portfolio API admin"
admin.site.site_title = "Portfolio API"

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", api_root, name="api-root"),
    path("api/", include("apps.core.urls")),
    path("api/contact/", include("apps.contact.urls")),
    path("api/projects/", include("apps.projects.urls")),
    path("api/guestbook/", include("apps.guestbook.urls")),
    path("api/auth/", include("apps.accounts.urls")),
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
    path("api/redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"),
]
