from datetime import datetime, timedelta

from django.utils import timezone

from RestaurantApp.forms import RegistrationForm, ReservationForm
from RestaurantApp.models import User


def test_registration_form_rejects_mismatched_passwords(db):
    form = RegistrationForm(
        {
            "name": "Alice",
            "login": "alice",
            "password": "secret-password",
            "password_confirmation": "different-password",
        }
    )

    assert not form.is_valid()
    assert "password_confirmation" in form.errors


def test_registration_form_rejects_an_existing_login(db):
    User.objects.create(name="Alice", login="alice", password="hash")

    form = RegistrationForm(
        {
            "name": "Another Alice",
            "login": "alice",
            "password": "secret-password",
            "password_confirmation": "secret-password",
        }
    )

    assert not form.is_valid()
    assert "login" in form.errors


def test_registration_form_rejects_a_numeric_password(db):
    form = RegistrationForm(
        {
            "name": "Alice",
            "login": "alice",
            "password": "12345678",
            "password_confirmation": "12345678",
        }
    )

    assert not form.is_valid()
    assert "password" in form.errors


def test_reservation_form_rejects_a_date_more_than_fourteen_days_away():
    form = ReservationForm(
        {
            "name": "Guest",
            "guest_count": 2,
            "date": timezone.localdate() + timedelta(days=15),
            "timeslot": "11:00",
        },
        max_capacity=4,
    )

    assert not form.is_valid()
    assert "date" in form.errors


def test_reservation_form_rejects_a_party_larger_than_any_table():
    form = ReservationForm(
        {
            "name": "Guest",
            "guest_count": 5,
            "date": timezone.localdate() + timedelta(days=1),
            "timeslot": "11:00",
        },
        max_capacity=4,
    )

    assert not form.is_valid()
    assert "guest_count" in form.errors


def test_reservation_form_rejects_a_past_date():
    form = ReservationForm(
        {
            "name": "Guest",
            "guest_count": 2,
            "date": timezone.localdate() - timedelta(days=1),
            "timeslot": "11:00",
        },
        max_capacity=4,
    )

    assert not form.is_valid()
    assert "date" in form.errors


def test_reservation_form_rejects_a_timeslot_that_has_already_started(monkeypatch):
    monkeypatch.setattr(
        "RestaurantApp.forms.timezone.localtime", lambda: datetime(2026, 7, 24, 15, 30)
    )
    monkeypatch.setattr(
        "RestaurantApp.forms.timezone.localdate", lambda: datetime(2026, 7, 24).date()
    )
    form = ReservationForm(
        {"name": "Guest", "guest_count": 2, "date": "2026-07-24", "timeslot": "15:00"},
        max_capacity=4,
    )

    assert not form.is_valid()
    assert "timeslot" in form.errors
