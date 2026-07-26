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
- PostgreSQL for Render production deployment
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

Apply the database migrations:

```bash
uv run python manage.py migrate
```

Check the Django project configuration:

```bash
uv run python manage.py check
```

## Run the development server

```bash
uv run python manage.py runserver
```

Then open <http://127.0.0.1:8000/> in a browser.

## Testing

Run the test suite:

```bash
uv run pytest
```

Run the test suite with coverage:

```bash
uv run coverage run -m pytest
uv run coverage report
```

Generate an HTML coverage report if needed:

```bash
uv run coverage html
```

## Code quality

Check formatting with Black:

```bash
uv run black --fast --check .
```

Run Pylint on the Django project and application:

```bash
uv run pylint Restaurant RestaurantApp
```

## Render deployment

The production deployment uses Render Web Service, Render PostgreSQL,
Waitress, and WhiteNoise. Production reservations use PostgreSQL through the
`DATABASE_URL` environment variable; local development continues to use
SQLite when that variable is not set.

### Environment variables

Set the following values in the Render Web Service settings:

- `SECRET_KEY`: generate a secret value in Render.
- `DATABASE_URL`: the internal connection URL of the Render PostgreSQL database.

Render automatically provides `RENDER` and `RENDER_EXTERNAL_HOSTNAME`.
The application uses them to set `DEBUG=False` and `ALLOWED_HOSTS` in
production. Render terminates HTTPS and forwards `X-Forwarded-Proto`; Django
uses that trusted header to preserve the HTTPS scheme for CSRF-protected POST
requests.

### Render commands

Create a PostgreSQL database and Web Service in the Render dashboard, then
configure these commands for the Web Service:

```text
Build Command: uv sync --frozen && uv run python manage.py migrate && uv run python manage.py collectstatic --noinput
Start Command: uv run waitress-serve --host=0.0.0.0 --port=$PORT Restaurant.wsgi:application
```

The `0002_create_initial_restaurant_tables` data migration creates the 20
restaurant tables when `uv run python manage.py migrate` runs. The application
does not use uploaded files or images, so no media-file storage is configured.
