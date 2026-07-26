import os
import subprocess
import sys

from django.conf import settings
from django.contrib.auth.hashers import make_password
from django.test import Client, override_settings
from django.urls import reverse

from RestaurantApp.models import RestaurantTable, User


def test_static_files_have_a_production_collection_directory():
    assert settings.STATIC_ROOT == settings.BASE_DIR / "staticfiles"


def test_render_settings_require_a_secret_key():
    environment = os.environ | {
        "RENDER": "1",
        "RENDER_EXTERNAL_HOSTNAME": "restaurant.example.onrender.com",
    }
    environment.pop("SECRET_KEY", None)

    result = subprocess.run(
        [sys.executable, "-c", "from Restaurant import settings"],
        check=False,
        capture_output=True,
        env=environment,
        text=True,
    )

    assert result.returncode != 0
    assert "SECRET_KEY" in result.stderr


def test_render_settings_trust_render_forwarded_https_scheme():
    environment = os.environ | {
        "RENDER": "1",
        "RENDER_EXTERNAL_HOSTNAME": "restaurant.example.onrender.com",
        "SECRET_KEY": "test-secret-key",
    }

    result = subprocess.run(
        [
            sys.executable,
            "-c",
            "from Restaurant import settings; print(settings.SECURE_PROXY_SSL_HEADER)",
        ],
        check=False,
        capture_output=True,
        env=environment,
        text=True,
    )

    assert result.returncode == 0
    assert result.stdout.strip() == "('HTTP_X_FORWARDED_PROTO', 'https')"


def test_render_settings_trust_render_external_origin():
    environment = os.environ | {
        "RENDER": "1",
        "RENDER_EXTERNAL_HOSTNAME": "restaurant.example.onrender.com",
        "SECRET_KEY": "test-secret-key",
    }

    result = subprocess.run(
        [
            sys.executable,
            "-c",
            "from Restaurant import settings; print(settings.CSRF_TRUSTED_ORIGINS)",
        ],
        check=False,
        capture_output=True,
        env=environment,
        text=True,
    )

    assert result.returncode == 0
    assert result.stdout.strip() == "['https://restaurant.example.onrender.com']"


@override_settings(SECURE_PROXY_SSL_HEADER=("HTTP_X_FORWARDED_PROTO", "https"))
def test_forwarded_https_login_post_passes_csrf_validation(db):
    user = User.objects.create(
        name="Alice", login="alice", password=make_password("secret-password")
    )
    client = Client(enforce_csrf_checks=True)
    login_url = reverse("login")
    response = client.get(
        login_url,
        HTTP_HOST="testserver",
        HTTP_X_FORWARDED_PROTO="https",
    )

    response = client.post(
        login_url,
        {
            "login": user.login,
            "password": "secret-password",
            "csrfmiddlewaretoken": response.cookies["csrftoken"].value,
        },
        HTTP_HOST="testserver",
        HTTP_ORIGIN="https://testserver",
        HTTP_X_FORWARDED_PROTO="https",
    )

    assert response.status_code == 302


def test_migrations_create_the_initial_restaurant_tables(db):
    tables = RestaurantTable.objects.order_by("number")

    assert tables.count() == 20
    assert list(tables.values_list("number", "capacity")) == [
        (1, 2),
        (2, 2),
        (3, 2),
        (4, 2),
        (5, 4),
        (6, 4),
        (7, 4),
        (8, 4),
        (9, 6),
        (10, 6),
        (11, 6),
        (12, 6),
        (13, 8),
        (14, 8),
        (15, 8),
        (16, 8),
        (17, 10),
        (18, 10),
        (19, 10),
        (20, 10),
    ]
