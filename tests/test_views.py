from datetime import date, time

import pytest
from django.urls import reverse

from RestaurantApp.models import Reservation, RestaurantTable, User


@pytest.mark.django_db
def test_home_returns_application_name(client):
    response = client.get(reverse("home"))

    assert response.status_code == 200
    assert response["Content-Type"].startswith("text/plain")
    assert "Fancy Restaurant" in response.content.decode()


@pytest.mark.django_db
def test_table_list_returns_restaurant_tables(client):
    RestaurantTable.objects.create(number=1, capacity=2)
    RestaurantTable.objects.create(number=2, capacity=4)

    response = client.get(reverse("table-list"))

    assert response.status_code == 200
    assert response["Content-Type"].startswith("text/plain")
    assert "Table 1 (2 seats)" in response.content.decode()
    assert "Table 2 (4 seats)" in response.content.decode()


@pytest.mark.django_db
def test_reservation_list_returns_reservations(client):
    user = User.objects.create(name="John", login="john", password="password")
    table = RestaurantTable.objects.create(number=1, capacity=4)
    Reservation.objects.create(
        user=user,
        table=table,
        guest_count=2,
        date=date(2026, 7, 23),
        start_time=time(18, 0),
        end_time=time(20, 0),
    )

    response = client.get(reverse("reservation-list"))

    assert response.status_code == 200
    assert response["Content-Type"].startswith("text/plain")
    assert "John, 2 people, Table 1 (4 seats)" in response.content.decode()
