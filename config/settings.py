"""
Django settings for the portfolio API.

Every secret and environment-specific value comes from environment variables
(see .env.example). DEBUG defaults to False so a missing variable never exposes
debug pages in production.
"""
from datetime import timedelta
from pathlib import Path

import environ

BASE_DIR = Path(__file__).resolve().parent.parent

env = environ.Env(
    DEBUG=(bool, False),
    ALLOWED_HOSTS=(list, []),
    CORS_ALLOWED_ORIGINS=(list, []),
    CSRF_TRUSTED_ORIGINS=(list, []),
    NUM_PROXIES=(int, 0),
    GUESTBOOK_AUTO_APPROVE=(bool, True),
)
environ.Env.read_env(BASE_DIR / ".env")

DEBUG = env("DEBUG")

if DEBUG:
    SECRET_KEY = env("SECRET_KEY", default="dev-only-insecure-key-do-not-use-in-production")
else:
    SECRET_KEY = env("SECRET_KEY")  # required: raises ImproperlyConfigured when missing

ALLOWED_HOSTS = env("ALLOWED_HOSTS") or (["localhost", "127.0.0.1"] if DEBUG else [])
# Render injects the public hostname of the service.
RENDER_EXTERNAL_HOSTNAME = env("RENDER_EXTERNAL_HOSTNAME", default="")
if RENDER_EXTERNAL_HOSTNAME:
    ALLOWED_HOSTS.append(RENDER_EXTERNAL_HOSTNAME)

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # third party
    "corsheaders",
    "rest_framework",
    "rest_framework_simplejwt",
    "drf_spectacular",
    # local
    "apps.core",
    "apps.contact",
    "apps.projects",
    "apps.guestbook",
    "apps.accounts",
]

MIDDLEWARE = [
    "apps.core.middleware.ResponseTimeMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"

# --- Database -------------------------------------------------------------
# DATABASE_URL (PostgreSQL on Neon in production). Falls back to SQLite locally.
DATABASES = {
    "default": env.db("DATABASE_URL", default=f"sqlite:///{BASE_DIR / 'db.sqlite3'}"),
}
DATABASES["default"]["CONN_MAX_AGE"] = env.int("CONN_MAX_AGE", default=60)
DATABASES["default"]["CONN_HEALTH_CHECKS"] = True

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# --- Cache ----------------------------------------------------------------
# No Redis on the free tier: the database cache is shared between gunicorn
# workers (unlike LocMem). Table is created with `manage.py createcachetable`.
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.db.DatabaseCache",
        "LOCATION": "api_cache",
        "TIMEOUT": 300,
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "en-us"
TIME_ZONE = "Europe/Belgrade"  # same zone as Pristina
USE_I18N = True
USE_TZ = True

# --- Static files (admin + API docs assets) served by WhiteNoise -----------
STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage"
        if not DEBUG
        else "django.contrib.staticfiles.storage.StaticFilesStorage"
    },
}

# --- CORS: only the portfolio frontend may call the API from a browser -----
CORS_ALLOWED_ORIGINS = env("CORS_ALLOWED_ORIGINS")
if env("CORS_ALLOWED_ORIGIN_REGEX", default=""):
    CORS_ALLOWED_ORIGIN_REGEXES = [env("CORS_ALLOWED_ORIGIN_REGEX")]
CORS_URLS_REGEX = r"^/api/.*$"
CORS_EXPOSE_HEADERS = ["Retry-After", "X-Response-Time-Ms", "X-Cache"]
CSRF_TRUSTED_ORIGINS = env("CSRF_TRUSTED_ORIGINS")

# --- Security (production) -----------------------------------------------
if not DEBUG:
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
    SECURE_SSL_REDIRECT = env.bool("SECURE_SSL_REDIRECT", default=True)
    SECURE_REDIRECT_EXEMPT = [r"^api/health/$"]
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_HSTS_SECONDS = 60 * 60 * 24 * 30
    SECURE_HSTS_INCLUDE_SUBDOMAINS = False
    SECURE_CONTENT_TYPE_NOSNIFF = True
    SECURE_REFERRER_POLICY = "strict-origin-when-cross-origin"
    X_FRAME_OPTIONS = "DENY"
    # The API lives on a shared host (*.onrender.com) whose subdomains we don't control,
    # so HSTS subdomains/preload must stay off.
    SILENCED_SYSTEM_CHECKS = ["security.W005", "security.W021"]

# --- Django REST Framework -------------------------------------------------
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": ["rest_framework.permissions.AllowAny"],
    "DEFAULT_RENDERER_CLASSES": ["rest_framework.renderers.JSONRenderer"]
    + (["rest_framework.renderers.BrowsableAPIRenderer"] if DEBUG else []),
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    "DEFAULT_THROTTLE_CLASSES": [
        "rest_framework.throttling.AnonRateThrottle",
        "rest_framework.throttling.ScopedRateThrottle",
    ],
    "DEFAULT_THROTTLE_RATES": {
        "anon": env("THROTTLE_ANON", default="600/hour"),
        "contact": env("THROTTLE_CONTACT", default="5/hour"),
        "guestbook": env("THROTTLE_GUESTBOOK", default="10/hour"),
        "stats": env("THROTTLE_STATS", default="120/hour"),
        "auth": env("THROTTLE_AUTH", default="20/hour"),
    },
    # Behind Render's proxy the real client IP is in X-Forwarded-For.
    "NUM_PROXIES": env("NUM_PROXIES") or None,
    "TEST_REQUEST_DEFAULT_FORMAT": "json",
}

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=10),
    "REFRESH_TOKEN_LIFETIME": timedelta(hours=12),
    "AUTH_HEADER_TYPES": ("Bearer",),
    "UPDATE_LAST_LOGIN": False,
}

SPECTACULAR_SETTINGS = {
    "TITLE": "Atlantik Jashari – Portfolio API",
    "DESCRIPTION": (
        "Live Django REST Framework backend behind atlantik's portfolio "
        "Backend Lab: contact form, projects, guestbook, analytics, JWT demo and health."
    ),
    "VERSION": "1.0.0",
    "SERVE_INCLUDE_SCHEMA": False,
    "COMPONENT_SPLIT_REQUEST": True,
    "SWAGGER_UI_SETTINGS": {"persistAuthorization": True, "displayRequestDuration": True},
}

# --- App settings ------------------------------------------------------------
RESEND_API_KEY = env("RESEND_API_KEY", default="")
RESEND_FROM = env("RESEND_FROM", default="Portfolio <onboarding@resend.dev>")
CONTACT_NOTIFY_EMAIL = env("CONTACT_NOTIFY_EMAIL", default="")
DEMO_USERNAME = env("DEMO_USERNAME", default="demo")
DEMO_PASSWORD = env("DEMO_PASSWORD", default="demo-portfolio-2026")
GUESTBOOK_AUTO_APPROVE = env("GUESTBOOK_AUTO_APPROVE")
STATS_CACHE_SECONDS = env.int("STATS_CACHE_SECONDS", default=60)
APP_VERSION = env("RENDER_GIT_COMMIT", default="dev")[:7]

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {"console": {"class": "logging.StreamHandler"}},
    "root": {"handlers": ["console"], "level": env("LOG_LEVEL", default="INFO")},
}
