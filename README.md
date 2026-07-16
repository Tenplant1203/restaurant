# Fancy Restaurant

This is the SA01 course project: a Django-based restaurant reservation system.

The application allows a user to request a restaurant table by specifying the
number of guests, a desired date, and a desired timeslot. The system checks
table availability, creates a reservation when possible, and suggests a
nearby available timeslot when the requested slot is unavailable.

## Project documentation

The original project proposal was submitted as Exercise 1 and Exercise 2.
The current project documentation is maintained here:

- [Functional specification](docs/functional-spec.md)
- [Technical specification](docs/technical-spec.md)

The functional specification describes the user-facing reservation flow. The
technical specification describes the implementation approach and the current
technical state of the project.

## Planned user flow

1. The user enters the number of guests, date, and desired timeslot.
2. The system checks the availability of suitable restaurant tables.
3. If a table is available, the system creates the reservation.
4. If the requested timeslot is unavailable, the system suggests the closest
   available timeslot on the same day.
5. If the whole day is booked, the system suggests the closest available slot
   on a nearby day.
6. The system displays the result of the reservation request.

User authentication may be used to identify returning users. For guests, the
reservation flow can request the necessary name or contact information.

## Technology

- Python 3.11+
- Django 5
- SQLite for local development
- uv for dependency and virtual-environment management
- pytest and pytest-django for testing
- coverage.py for test coverage
- Black for formatting
- Pylint and pylint-django for linting

## Project status

The development environment and initial Django project/app structure are in
place. The reservation models, forms, views, templates, dynamic interactions,
and application tests are being developed incrementally.

## Setup

Install the project dependencies with uv:

```bash
uv sync
```

Activate the virtual environment:

```bash
source .venv/bin/activate
```

Apply the database migrations:

```bash
python manage.py migrate
```

Check the Django project configuration:

```bash
python manage.py check
```

## Run the development server

```bash
python manage.py runserver
```

Then open <http://127.0.0.1:8000/> in a browser.

## Testing

Run the test suite:

```bash
pytest
```

Run the test suite with coverage:

```bash
coverage run -m pytest
coverage report
```

Generate an HTML coverage report if needed:

```bash
coverage html
```

## Code quality

Check formatting with Black:

```bash
black --check .
```

Run Pylint on the Django project and application:

```bash
pylint Restaurant RestaurantApp
```
