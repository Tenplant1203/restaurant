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

Activate the virtual environment:

```bash
source .venv/bin/activate
```

Apply database migrations:

```bash
python manage.py migrate
```

Check the Django project configuration:

```bash
python manage.py check
```

Start the development server:

```bash
python manage.py runserver
```

Open <http://127.0.0.1:8000/> in a browser.

## Tests

Run tests:

```bash
uv run pytest
```

Run tests with coverage:

```bash
uv run coverage run -m pytest
uv run coverage report
```

## Development and CI commands

Install the locked dependencies:

```bash
uv sync --locked
```

Check the Django project:

```bash
uv run python manage.py check
```

Check for model changes without migration files:

```bash
uv run python manage.py makemigrations --check --dry-run
```

Check code formatting:

```bash
uv run black --check .
```

Run the linter:

```bash
uv run pylint Restaurant RestaurantApp
```

Run tests with coverage:

```bash
uv run coverage run -m pytest
uv run coverage report
```
