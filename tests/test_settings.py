from django.conf import settings


def test_restaurant_uses_japan_time_as_default():
    assert settings.TIME_ZONE == "Asia/Tokyo"
