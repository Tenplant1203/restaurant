from dataclasses import dataclass
from datetime import date, time
from uuid import uuid4

from django.contrib.auth.hashers import make_password
from django.db import transaction
from django.utils import timezone

from RestaurantApp.models import Reservation, RestaurantTable, Status, User

TIME_SLOT_VALUES = tuple(f"{hour:02d}:00" for hour in range(11, 21))


@dataclass(frozen=True)
class ReservationDetails:
    guest_count: int
    reservation_date: date
    start_time: time
    end_time: time


def timeslot_bounds(timeslot):
    start_time = time.fromisoformat(timeslot)
    return start_time, time(start_time.hour + 1, start_time.minute)


def find_available_table(reservation_date, start_time, end_time, guest_count):
    occupied_table_ids = Reservation.objects.filter(
        date=reservation_date,
        status__in=[Status.PENDING, Status.CONFIRMED],
        start_time__lt=end_time,
        end_time__gt=start_time,
    ).values("table_id")

    return (
        RestaurantTable.objects.filter(capacity__gte=guest_count)
        .exclude(pk__in=occupied_table_ids)
        .order_by("capacity", "number")
        .first()
    )


def create_guest_user(name):
    guest_identifier = uuid4().hex
    return User.objects.create(
        name=name,
        login=f"guest-{guest_identifier}",
        password=make_password(uuid4().hex),
    )


@transaction.atomic
def create_confirmed_reservation(user, table, details):
    return Reservation.objects.create(
        user=user,
        table=table,
        guest_count=details.guest_count,
        date=details.reservation_date,
        start_time=details.start_time,
        end_time=details.end_time,
        status=Status.CONFIRMED,
    )


def find_nearest_available_timeslot(reservation_date, requested_timeslot, guest_count):
    requested_start, _ = timeslot_bounds(requested_timeslot)
    candidates = sorted(
        TIME_SLOT_VALUES,
        key=lambda value: abs(
            (time.fromisoformat(value).hour - requested_start.hour) * 60
        ),
    )
    for timeslot in candidates:
        if timeslot == requested_timeslot:
            continue
        start_time, end_time = timeslot_bounds(timeslot)
        if (
            reservation_date == timezone.localdate()
            and start_time <= timezone.localtime().time()
        ):
            continue
        if find_available_table(reservation_date, start_time, end_time, guest_count):
            return timeslot
    return None
