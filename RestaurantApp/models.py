from django.db import models


class Status(models.TextChoices):  # pylint: disable=too-many-ancestors
    PENDING = "pending", "Pending"
    CONFIRMED = "confirmed", "Confirmed"
    CANCELLED = "cancelled", "Cancelled"


class User(models.Model):
    name = models.CharField(max_length=20)
    login = models.CharField(max_length=20, unique=True)
    password = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class Reservation(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    guest_count = models.PositiveIntegerField()
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    status = models.CharField(
        max_length=10, choices=Status.choices, default=Status.PENDING
    )
    table = models.ForeignKey("RestaurantTable", on_delete=models.CASCADE)

    def __str__(self):
        return (
            f"{self.user.name}, "
            f"{self.guest_count} people, "
            f"{self.table}, "
            f"{self.date}, "
            f"{self.start_time}~{self.end_time}, "
            f"status: {self.status}"
        )


class RestaurantTable(models.Model):
    number = models.PositiveIntegerField(unique=True)
    capacity = models.PositiveIntegerField()

    def __str__(self):
        return f"Table {self.number} ({self.capacity} seats)"
