from datetime import date, time, timedelta

import pytest
from django.contrib.auth.hashers import check_password, make_password
from django.urls import reverse
from django.utils import timezone

from RestaurantApp.models import Reservation, RestaurantTable, User


@pytest.fixture(autouse=True)
def clear_initial_restaurant_tables(db):
    RestaurantTable.objects.all().delete()


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
@pytest.mark.parametrize("url_name", ["login", "register"])
def test_login_and_register_keep_logged_in_navigation(client, url_name):
    user = User.objects.create(name="Alice", login="alice", password="hash")
    session = client.session
    session["user_login"] = user.login
    session.save()

    response = client.get(reverse(url_name))

    assert 'href="/reservations/">My reservations</a>' in response.content.decode()
    assert 'action="/logout/"' in response.content.decode()


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
    content = response.content.decode()

    assert response.status_code == 200
    assert response["Content-Type"].startswith("text/html")
    assert "Fancy Restaurant" in content
    assert "New reservation" in content
    assert '<section class="app-shell">' in content
    assert '<section class="booking-card">' in content
    assert 'button type="submit">Reserve a table' in content
    assert reverse("table-list") not in content


@pytest.mark.django_db
def test_home_loads_the_responsive_stylesheet(client):
    response = client.get(reverse("home"))
    content = response.content.decode()

    assert (
        '<meta name="viewport" content="width=device-width, initial-scale=1">'
        in content
    )
    assert 'href="/static/RestaurantApp/style.css"' in content


@pytest.mark.django_db
def test_home_configures_htmx_availability_updates(client):
    response = client.get(reverse("home"))
    content = response.content.decode()
    form = response.context["form"]

    assert 'src="/static/RestaurantApp/htmx.min.js"' in content
    assert "X-CSRFToken" in content
    for field_name in ("guest_count", "date", "timeslot"):
        widget_attrs = form.fields[field_name].widget.attrs
        assert widget_attrs["hx-post"] == reverse("reservation-availability")
        assert widget_attrs["hx-target"] == "#availability-result"
    assert 'id="availability-result"' in content


@pytest.mark.django_db
def test_availability_returns_guidance_when_required_inputs_are_missing(client):
    response = client.post(
        reverse("reservation-availability"),
        {"guest_count": 2},
        HTTP_HX_REQUEST="true",
    )

    assert response.status_code == 200
    assert "Enter the number of guests, date, and timeslot to check availability." in (
        response.content.decode()
    )


@pytest.mark.django_db
def test_availability_rejects_get_requests(client):
    response = client.get(reverse("reservation-availability"))

    assert response.status_code == 405


@pytest.mark.django_db
def test_availability_reports_when_the_requested_timeslot_is_available(client):
    RestaurantTable.objects.create(number=1, capacity=2)

    response = client.post(
        reverse("reservation-availability"),
        {
            "guest_count": 2,
            "date": timezone.localdate() + timedelta(days=1),
            "timeslot": "11:00",
        },
        HTTP_HX_REQUEST="true",
    )

    assert response.status_code == 200
    assert "This timeslot is available." in response.content.decode()
    assert not Reservation.objects.exists()


@pytest.mark.django_db
def test_availability_suggests_the_nearest_available_timeslot(client):
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
        status="confirmed",
    )

    response = client.post(
        reverse("reservation-availability"),
        {"guest_count": 2, "date": reservation_date, "timeslot": "11:00"},
        HTTP_HX_REQUEST="true",
    )

    assert response.status_code == 200
    assert "Try 12:00 instead." in response.content.decode()


@pytest.mark.django_db
def test_availability_reports_when_the_day_is_fully_booked(client):
    user = User.objects.create(name="Alice", login="alice", password="hash")
    table = RestaurantTable.objects.create(number=1, capacity=2)
    reservation_date = timezone.localdate() + timedelta(days=1)
    for hour in range(11, 21):
        Reservation.objects.create(
            user=user,
            table=table,
            guest_count=2,
            date=reservation_date,
            start_time=time(hour, 0),
            end_time=time(hour + 1, 0),
            status="confirmed",
        )

    response = client.post(
        reverse("reservation-availability"),
        {"guest_count": 2, "date": reservation_date, "timeslot": "11:00"},
        HTTP_HX_REQUEST="true",
    )

    assert response.status_code == 200
    assert "This day is fully booked." in response.content.decode()


@pytest.mark.django_db
def test_availability_returns_a_validation_message_for_an_invalid_date(client):
    RestaurantTable.objects.create(number=1, capacity=2)

    response = client.post(
        reverse("reservation-availability"),
        {
            "guest_count": 2,
            "date": timezone.localdate() + timedelta(days=15),
            "timeslot": "11:00",
        },
        HTTP_HX_REQUEST="true",
    )

    assert response.status_code == 200
    assert "Reservations can only be made within 14 days." in response.content.decode()


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
def test_reservation_list_redirects_guests_to_login(client):
    response = client.get(reverse("reservation-list"))

    assert response.status_code == 302
    assert response.url == reverse("login")


@pytest.mark.django_db
def test_home_hides_reservations_navigation_for_guests(client):
    response = client.get(reverse("home"))

    assert 'href="/reservations/">Reservations</a>' not in response.content.decode()


@pytest.mark.django_db
def test_home_shows_reservations_navigation_for_logged_in_users(client):
    user = User.objects.create(name="John", login="john", password="password")
    session = client.session
    session["user_login"] = user.login
    session.save()

    response = client.get(reverse("home"))

    assert 'href="/reservations/">My reservations</a>' in response.content.decode()


@pytest.mark.django_db
def test_reservation_list_shows_an_empty_message(client):
    user = User.objects.create(name="John", login="john", password="password")
    session = client.session
    session["user_login"] = user.login
    session.save()

    response = client.get(reverse("reservation-list"))

    assert "No reservations yet" in response.content.decode()


@pytest.mark.django_db
def test_reservation_list_shows_only_logged_in_users_reservations(client):
    user = User.objects.create(name="John", login="john", password="password")
    other_user = User.objects.create(name="Jane", login="jane", password="password")
    table = RestaurantTable.objects.create(number=1, capacity=4)
    Reservation.objects.create(
        user=user,
        table=table,
        guest_count=2,
        date=date(2026, 7, 23),
        start_time=time(18, 0),
        end_time=time(20, 0),
    )
    Reservation.objects.create(
        user=other_user,
        table=table,
        guest_count=3,
        date=date(2026, 7, 24),
        start_time=time(19, 0),
        end_time=time(21, 0),
    )
    Reservation.objects.create(
        user=user,
        table=table,
        guest_count=4,
        date=date(2026, 7, 24),
        start_time=time(17, 0),
        end_time=time(19, 0),
    )
    session = client.session
    session["user_login"] = user.login
    session.save()

    response = client.get(reverse("reservation-list"))

    assert response.status_code == 200
    assert response["Content-Type"].startswith("text/html")
    content = response.content.decode()
    assert "John, 2 people, Table 1 (4 seats)" in content
    assert "Jane, 3 people, Table 1 (4 seats)" not in content
    assert content.index("John, 4 people") < content.index("John, 2 people")
