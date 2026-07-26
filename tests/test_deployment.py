import os
import subprocess
import sys

from django.conf import settings

from RestaurantApp.models import RestaurantTable


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
