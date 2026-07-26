from datetime import date, datetime, time, timedelta

import pytest
from django.utils import timezone

from RestaurantApp.models import Reservation, RestaurantTable, Status, User
from RestaurantApp.services import (
    ReservationDetails,
    create_confirmed_reservation,
    find_available_table,
    find_nearest_available_timeslot,
    timeslot_bounds,
)


@pytest.fixture(autouse=True)
def clear_initial_restaurant_tables(db):
    RestaurantTable.objects.all().delete()


@pytest.mark.django_db
def test_find_available_table_selects_the_smallest_suitable_table():
    RestaurantTable.objects.create(number=1, capacity=4)
    smallest_table = RestaurantTable.objects.create(number=2, capacity=2)

    table = find_available_table(
        reservation_date=date(2026, 7, 25),
        start_time=time(11, 0),
        end_time=time(12, 0),
        guest_count=2,
    )

    assert table == smallest_table


@pytest.mark.django_db
def test_find_available_table_ignores_a_table_with_a_confirmed_reservation():
    user = User.objects.create(name="Alice", login="alice", password="hash")
    occupied_table = RestaurantTable.objects.create(number=1, capacity=2)
    available_table = RestaurantTable.objects.create(number=2, capacity=4)
    Reservation.objects.create(
        user=user,
        table=occupied_table,
        guest_count=2,
        date=date(2026, 7, 25),
        start_time=time(11, 0),
        end_time=time(12, 0),
        status=Status.CONFIRMED,
    )

    table = find_available_table(
        reservation_date=date(2026, 7, 25),
        start_time=time(11, 0),
        end_time=time(12, 0),
        guest_count=2,
    )

    assert table == available_table


def test_timeslot_bounds_returns_the_one_hour_interval():
    assert timeslot_bounds("11:00") == (time(11, 0), time(12, 0))


@pytest.mark.django_db
def test_create_confirmed_reservation_saves_the_reservation():
    user = User.objects.create(name="Alice", login="alice", password="hash")
    table = RestaurantTable.objects.create(number=1, capacity=2)

    reservation = create_confirmed_reservation(
        user=user,
        table=table,
        details=ReservationDetails(
            guest_count=2,
            reservation_date=date(2026, 7, 25),
            start_time=time(11, 0),
            end_time=time(12, 0),
        ),
    )

    assert reservation.status == Status.CONFIRMED
    assert Reservation.objects.get() == reservation


@pytest.mark.django_db
def test_find_nearest_available_timeslot_suggests_the_closest_slot():
    user = User.objects.create(name="Alice", login="alice", password="hash")
    table = RestaurantTable.objects.create(number=1, capacity=2)
    reservation_date = timezone.localdate() + timedelta(days=1)
    Reservation.objects.create(
        user=user,
        table=table,
        guest_count=2,
        date=reservation_date,
        start_time=time(11, 0),
        end_time=time(12, 0),
        status=Status.CONFIRMED,
    )

    suggestion = find_nearest_available_timeslot(
        reservation_date=reservation_date, requested_timeslot="11:00", guest_count=2
    )

    assert suggestion == "12:00"


@pytest.mark.django_db
def test_find_nearest_available_timeslot_skips_started_slots_today(monkeypatch):
    monkeypatch.setattr(
        "RestaurantApp.services.timezone.localdate", lambda: date(2026, 7, 25)
    )
    monkeypatch.setattr(
        "RestaurantApp.services.timezone.localtime",
        lambda: datetime(2026, 7, 25, 15, 30),
    )
    user = User.objects.create(name="Alice", login="alice", password="hash")
    table = RestaurantTable.objects.create(number=1, capacity=2)
    for hour in range(16, 21):
        Reservation.objects.create(
            user=user,
            table=table,
            guest_count=2,
            date=date(2026, 7, 25),
            start_time=time(hour, 0),
            end_time=time(hour + 1, 0),
            status=Status.CONFIRMED,
        )

    suggestion = find_nearest_available_timeslot(date(2026, 7, 25), "17:00", 2)

    assert suggestion is None
