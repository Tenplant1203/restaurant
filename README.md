# Restaurant

This is the course project for SA01.

## Project outline

This project is a Django-based restaurant reservation system.

The user can book a table in a restaurant. The user enters the number of guests, chooses a desired date and timeslot, and confirms the booking.

If the desired timeslot is not available, the system suggests the closest available timeslot.

## Main data entities

- User
- RestaurantTable
- Reservation

## Development environment

This project uses:

- Python 3.11
- Django
- uv

## Development tools

This project uses the following tools:

- Black for code formatting
- Pylint for linting
- pytest for testing
- coverage.py for coverage measurement

## Setup

Install dependencies:

```bash
uv sync
```
