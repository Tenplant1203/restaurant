# AGENTS.md

## Project scope

This is a Django application for managing restaurant table reservations.

Main components:

- `Restaurant/` — Django project configuration
- `RestaurantApp/` — restaurant reservation application
- `docs/` — functional and technical documentation

## Important project conventions

- Keep reservation and table-availability logic separate from presentation code where practical.
- Keep views focused on handling requests and responses.
- Keep reusable validation and input-handling logic in forms.
- Update the relevant documentation when the application behavior or technical design changes.

## Commands

- Run server: `uv run python manage.py runserver`
- Check project: `uv run python manage.py check`
- Run tests: `uv run pytest`
- Create migrations: `uv run python manage.py makemigrations`
- Apply migrations: `uv run python manage.py migrate`
- Check formatting: `uv run black --check .`
- Run linter: `uv run pylint Restaurant RestaurantApp`

## Things that are easy to break

- Reservation availability checks
- Reservation status transitions
- URL and view connections
- Form validation
- Database relationships between users, tables, and reservations

## Change coupling

If you change:

- a model → also check migrations, admin, forms, views, and tests
- a URL → also check the corresponding view and templates
- reservation logic → also check availability checks and user-facing messages
- a form → also check validation, templates, and tests

## Constraints

- Do not edit old migrations; create a new migration instead.
- Do not change URL names or model field names without checking the documentation.
- Prefer small, targeted changes over broad refactors.
- Do not claim that an unimplemented feature is complete.

## Documentation use

- Use `docs/functional-spec.md` for user-facing behavior and workflows.
- Use `docs/technical-spec.md` for technical decisions and implementation details.
- Keep documentation up to date when the behavior or technical design changes.
- If the code and documentation are inconsistent, report the inconsistency and suggest a fix.

## Testing expectations

Add or update tests for:

- model behavior
- reservation availability
- form validation
- view responses
- URL routing
