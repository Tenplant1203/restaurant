from datetime import date, time, timedelta

import pytest
from django.contrib.auth.hashers import check_password, make_password
from django.urls import reverse
from django.utils import timezone

from RestaurantApp.models import Reservation, RestaurantTable, User


@pytest.mark.django_db
def test_register_creates_a_user_hashes_password_and_logs_in(client):
    response = client.post(
        reverse("register"),
        {
            "name": "Alice",
            "login": "alice",
            "password": "secret-password",
            "password_confirmation": "secret-password",
        },
    )

    user = User.objects.get(login="alice")

    assert response.status_code == 302
    assert response.url == reverse("home")
    assert check_password("secret-password", user.password)
    assert client.session["user_login"] == "alice"


@pytest.mark.django_db
def test_login_creates_a_session_for_valid_credentials(client):
    user = User.objects.create(
        name="Alice", login="alice", password=make_password("secret-password")
    )

    response = client.post(
        reverse("login"), {"login": user.login, "password": "secret-password"}
    )

    assert response.status_code == 302
    assert response.url == reverse("home")
    assert client.session["user_login"] == user.login


@pytest.mark.django_db
def test_login_get_renders_the_login_form(client):
    response = client.get(reverse("login"))

    assert response.status_code == 200
    assert "Login" in response.content.decode()


@pytest.mark.django_db
def test_logout_removes_the_login_session(client):
    session = client.session
    session["user_login"] = "alice"
    session.save()

    response = client.post(reverse("logout"))

    assert response.status_code == 302
    assert response.url == reverse("home")
    assert "user_login" not in client.session


@pytest.mark.django_db
def test_home_shows_logout_control_for_a_logged_in_user(client):
    user = User.objects.create(name="Alice", login="alice", password="hash")
    session = client.session
    session["user_login"] = user.login
    session.save()

    response = client.get(reverse("home"))

    assert "Alice" in response.content.decode()
    assert 'action="/logout/"' in response.content.decode()


@pytest.mark.django_db
def test_invalid_reservation_keeps_logout_control_for_a_logged_in_user(client):
    user = User.objects.create(name="Alice", login="alice", password="hash")
    RestaurantTable.objects.create(number=1, capacity=2)
    session = client.session
    session["user_login"] = user.login
    session.save()

    response = client.post(
        reverse("reservation-list"),
        {"name": "Alice", "guest_count": 0, "date": "2026-07-26", "timeslot": "11:00"},
    )

    assert response.status_code == 200
    assert 'action="/logout/"' in response.content.decode()


@pytest.mark.django_db
def test_reservation_post_creates_a_confirmed_reservation_for_a_guest(client):
    table = RestaurantTable.objects.create(number=1, capacity=2)
    reservation_date = timezone.localdate() + timedelta(days=1)

    response = client.post(
        reverse("reservation-list"),
        {
            "name": "Guest",
            "guest_count": 2,
            "date": reservation_date,
            "timeslot": "11:00",
        },
    )

    reservation = Reservation.objects.get()

    assert response.status_code == 302
    assert response.url == reverse("home")
    assert reservation.user.name == "Guest"
    assert reservation.table == table
    assert reservation.status == "confirmed"
    assert reservation.start_time == time(11, 0)
    assert reservation.end_time == time(12, 0)
    assert "user_login" not in client.session


@pytest.mark.django_db
def test_home_renders_the_reservation_form(client):
    response = client.get(reverse("home"))

    assert response.status_code == 200
    assert response["Content-Type"].startswith("text/html")
    assert "Fancy Restaurant" in response.content.decode()
    assert "New Reservation" in response.content.decode()
    assert reverse("table-list") not in response.content.decode()


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
