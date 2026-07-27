from datetime import time, timedelta

from django import forms
from django.contrib.auth.password_validation import validate_password
from django.urls import reverse
from django.utils import timezone

from RestaurantApp.models import User

TIME_SLOTS = tuple(
    (time(hour, 0).strftime("%H:%M"), f"{hour:02d}:00–{hour + 1:02d}:00")
    for hour in range(11, 21)
)


class RegistrationForm(forms.Form):
    name = forms.CharField(max_length=20)
    login = forms.CharField(max_length=20)
    password = forms.CharField(max_length=255, widget=forms.PasswordInput)
    password_confirmation = forms.CharField(max_length=255, widget=forms.PasswordInput)

    def clean_login(self):
        login = self.cleaned_data["login"]
        if User.objects.filter(login=login).exists():
            raise forms.ValidationError("This login is already in use.")
        return login

    def clean_password(self):
        password = self.cleaned_data["password"]
        validate_password(password)
        return password

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        password_confirmation = cleaned_data.get("password_confirmation")

        if password and password_confirmation and password != password_confirmation:
            self.add_error("password_confirmation", "Passwords do not match.")

        return cleaned_data


class LoginForm(forms.Form):
    login = forms.CharField(max_length=20)
    password = forms.CharField(max_length=255, widget=forms.PasswordInput)


class ReservationAvailabilityValidationMixin:
    def __init__(self, *args, max_capacity, **kwargs):
        super().__init__(*args, **kwargs)
        self.max_capacity = max_capacity

    def clean_guest_count(self):
        guest_count = self.cleaned_data["guest_count"]
        if guest_count > self.max_capacity:
            raise forms.ValidationError("The party is larger than any table.")
        return guest_count

    def clean_date(self):
        reservation_date = self.cleaned_data["date"]
        today = timezone.localdate()

        if reservation_date < today:
            raise forms.ValidationError("Reservations cannot be made in the past.")
        if reservation_date > today + timedelta(days=14):
            raise forms.ValidationError("Reservations can only be made within 14 days.")
        return reservation_date

    def clean(self):
        cleaned_data = super().clean()
        reservation_date = cleaned_data.get("date")
        timeslot = cleaned_data.get("timeslot")

        if reservation_date == timezone.localdate() and timeslot:
            start_time = time.fromisoformat(timeslot)
            if start_time <= timezone.localtime().time():
                self.add_error("timeslot", "This timeslot has already started.")

        return cleaned_data


class AvailabilityForm(ReservationAvailabilityValidationMixin, forms.Form):
    guest_count = forms.IntegerField(min_value=1)
    date = forms.DateField(widget=forms.DateInput(attrs={"type": "date"}))
    timeslot = forms.ChoiceField(choices=TIME_SLOTS)


class ReservationForm(ReservationAvailabilityValidationMixin, forms.Form):
    name = forms.CharField(max_length=20)
    guest_count = forms.IntegerField(min_value=1)
    date = forms.DateField(widget=forms.DateInput(attrs={"type": "date"}))
    timeslot = forms.ChoiceField(choices=TIME_SLOTS)

    def __init__(self, *args, max_capacity, user=None, **kwargs):
        super().__init__(*args, max_capacity=max_capacity, **kwargs)
        self.user = user

        for field_name in ("guest_count", "date", "timeslot"):
            self.fields[field_name].widget.attrs.update(
                {
                    "hx-post": reverse("reservation-availability"),
                    "hx-target": "#availability-result",
                }
            )

        if user is not None:
            self.fields["name"].initial = user.name
            self.fields["name"].widget.attrs["readonly"] = True
