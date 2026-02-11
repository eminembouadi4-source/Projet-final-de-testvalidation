from .settings import *

# Minimal settings for running unit tests without optional/admin tooling apps.
# Keep this file small and focused: only override what blocks test startup.

# Use a fast password hasher for tests
PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.MD5PasswordHasher",
]

# Disable third-party apps that are not required for unit tests and may not be installed.
_OPTIONAL_APPS_TO_REMOVE = {
    "sslserver",
    "django_admin_generator",
    "django_daisy",
}

INSTALLED_APPS = [app for app in INSTALLED_APPS if app not in _OPTIONAL_APPS_TO_REMOVE]

# Graphene can be optional; remove if schema isn't present during tests.
if "graphene_django" in INSTALLED_APPS:
    INSTALLED_APPS = [app for app in INSTALLED_APPS if app != "graphene_django"]

# Django REST Framework is not required for current unit tests; remove to avoid dependency issues.
if "rest_framework" in INSTALLED_APPS:
    INSTALLED_APPS = [app for app in INSTALLED_APPS if app != "rest_framework"]

# NOTE: Do not remove `cities_light`.
# The project models import `cities_light.models.City` directly (e.g. in `shop.models`).
# If the package isn't installed or the app isn't in INSTALLED_APPS, Django won't start.

# Disable cron app during unit tests.
if "django_cron" in INSTALLED_APPS:
    INSTALLED_APPS = [app for app in INSTALLED_APPS if app != "django_cron"]

# Use in-memory email backend for tests
EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"

# Use a test URLConf that does not require optional dependencies (e.g. DRF).
ROOT_URLCONF = "cooldeal.urls_test"
