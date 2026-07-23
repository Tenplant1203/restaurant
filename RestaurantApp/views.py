from django.http import HttpResponse

from RestaurantApp.models import Reservation, RestaurantTable


def home(request):
    message = "\n".join(
        ["Fancy Restaurant", "", "Available pages:", "- /tables/", "- /reservations/"]
    )
    return HttpResponse(message)


def table_list(request):
    tables = RestaurantTable.objects.all()
    table_details = "\n".join(str(table) for table in tables)
    return HttpResponse(table_details or "No tables available.")


def reservation_list(request):
    reservations = Reservation.objects.all()
    reservation_details = "\n".join(str(reservation) for reservation in reservations)
    return HttpResponse(reservation_details or "No reservations available.")
