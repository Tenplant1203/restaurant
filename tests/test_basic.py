from datetime import date, time
import pytest
from django.test import TestCase
from RestaurantApp.models import User, Reservation, RestaurantTable


@pytest.mark.django_db
def test_create_data():
    user = User(name="John", login="jonny", password="jpass")
    user.save()

    table = RestaurantTable(number=1, capacity=4)
    table.save()

    Reservation.objects.create(
        user=user,
        table=table,
        guest_count=2,
        date=date(2026, 7, 20),
        start_time=time(18, 0),
        end_time=time(20, 0),
    )

    assert User.objects.count() == 1
    assert RestaurantTable.objects.count() == 1
    assert Reservation.objects.count() == 1
