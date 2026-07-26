from django.contrib import messages
from django.contrib.auth.hashers import check_password, make_password
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.views.decorators.http import require_POST

from RestaurantApp.forms import (
    AvailabilityForm,
    LoginForm,
    RegistrationForm,
    ReservationForm,
)
from RestaurantApp.models import Reservation, RestaurantTable, User
from RestaurantApp.services import (
    ReservationDetails,
    create_confirmed_reservation,
    create_guest_user,
    find_available_table,
    find_nearest_available_timeslot,
    timeslot_bounds,
)


def home(request):
    user_login = request.session.get("user_login")
    user = User.objects.filter(login=user_login).first() if user_login else None
    max_capacity = (
        RestaurantTable.objects.order_by("-capacity")
        .values_list("capacity", flat=True)
        .first()
        or 0
    )
    form = ReservationForm(max_capacity=max_capacity, user=user)
    return render(
        request,
        "RestaurantApp/home.html",
        {"form": form, "user": user, "logged_in_user": user},
    )


@require_POST
def reservation_availability(request):
    max_capacity = (
        RestaurantTable.objects.order_by("-capacity")
        .values_list("capacity", flat=True)
        .first()
        or 0
    )
    required_fields = ("guest_count", "date", "timeslot")
    if not all(request.POST.get(field) for field in required_fields):
        return render(
            request,
            "RestaurantApp/availability_result.html",
            {
                "message": (
                    "Enter the number of guests, date, and timeslot to check availability."
                )
            },
        )

    form = AvailabilityForm(request.POST, max_capacity=max_capacity)
    if not form.is_valid():
        return render(
            request,
            "RestaurantApp/availability_result.html",
            {"errors": form.errors},
        )

    start_time, end_time = timeslot_bounds(form.cleaned_data["timeslot"])
    table = find_available_table(
        form.cleaned_data["date"],
        start_time,
        end_time,
        form.cleaned_data["guest_count"],
    )
    if table:
        message = "This timeslot is available."
    else:
        suggestion = find_nearest_available_timeslot(
            form.cleaned_data["date"],
            form.cleaned_data["timeslot"],
            form.cleaned_data["guest_count"],
        )
        message = (
            f"Try {suggestion} instead." if suggestion else "This day is fully booked."
        )
    return render(
        request,
        "RestaurantApp/availability_result.html",
        {"message": message},
    )


def table_list(request):
    tables = RestaurantTable.objects.all()
    table_details = "\n".join(str(table) for table in tables)
    return HttpResponse(
        table_details or "No tables available.", content_type="text/plain"
    )


def reservation_list(request):
    if request.method == "POST":
        user_login = request.session.get("user_login")
        user = User.objects.filter(login=user_login).first() if user_login else None
        max_capacity = (
            RestaurantTable.objects.order_by("-capacity")
            .values_list("capacity", flat=True)
            .first()
            or 0
        )
        form = ReservationForm(request.POST, max_capacity=max_capacity, user=user)
        if not form.is_valid():
            return render(
                request,
                "RestaurantApp/home.html",
                {"form": form, "user": user, "logged_in_user": user},
            )

        start_time, end_time = timeslot_bounds(form.cleaned_data["timeslot"])
        table = find_available_table(
            form.cleaned_data["date"],
            start_time,
            end_time,
            form.cleaned_data["guest_count"],
        )
        if table is None:
            suggestion = find_nearest_available_timeslot(
                form.cleaned_data["date"],
                form.cleaned_data["timeslot"],
                form.cleaned_data["guest_count"],
            )
            message = (
                f"Try {suggestion} instead."
                if suggestion
                else "This day is fully booked."
            )
            messages.error(request, message)
            return render(
                request,
                "RestaurantApp/home.html",
                {"form": form, "user": user, "logged_in_user": user},
            )

        reservation_user = user or create_guest_user(form.cleaned_data["name"])
        create_confirmed_reservation(
            reservation_user,
            table,
            ReservationDetails(
                guest_count=form.cleaned_data["guest_count"],
                reservation_date=form.cleaned_data["date"],
                start_time=start_time,
                end_time=end_time,
            ),
        )
        messages.success(request, "Reservation completed successfully.")
        return redirect("home")

    reservations = Reservation.objects.all()
    reservation_details = "\n".join(str(reservation) for reservation in reservations)
    return HttpResponse(
        reservation_details or "No reservations available.", content_type="text/plain"
    )


def register(request):
    form = RegistrationForm(request.POST or None)
    if request.method != "POST":
        return render(request, "RestaurantApp/register.html", {"form": form})
    if form.is_valid():
        user = User.objects.create(
            name=form.cleaned_data["name"],
            login=form.cleaned_data["login"],
            password=make_password(form.cleaned_data["password"]),
        )
        request.session["user_login"] = user.login
        messages.success(request, "Registration completed successfully.")
        return redirect("home")

    return render(request, "RestaurantApp/register.html", {"form": form}, status=400)


def login(request):
    form = LoginForm(request.POST or None)
    if request.method != "POST":
        return render(request, "RestaurantApp/login.html", {"form": form})

    user = User.objects.filter(login=form.data.get("login")).first()
    if (
        form.is_valid()
        and user
        and check_password(form.cleaned_data["password"], user.password)
    ):
        request.session["user_login"] = user.login
        messages.success(request, "Login successful.")
        return redirect("home")

    form.add_error(None, "Login or password is incorrect.")
    return render(request, "RestaurantApp/login.html", {"form": form}, status=400)


def logout(request):
    request.session.pop("user_login", None)
    messages.success(request, "Logged out successfully.")
    return redirect("home")
