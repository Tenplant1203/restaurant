# Technical Specification

## Application API

The application provides forms for registration, login, and reservation
creation.

| URL | Method | URL arguments | Request parameters | Response |
| --- | --- | --- | --- | --- |
| `/` | `GET` | None | None | HTML home page with the reservation form. |
| `/tables/` | `GET` | None | None | Plain-text list of restaurant tables, or a message when no tables exist. |
| `/reservations/` | `GET` | None | None | HTML page listing the logged-in user's reservations, newest first. Redirects to `/login/` when no logged-in user exists. |
| `/reservations/` | `POST` | None | Reservation form data | Creates a confirmed reservation or redisplays the form with an error or alternative timeslot. |
| `/availability/` | `POST` | None | Guest count, date, and timeslot | Returns an HTML fragment describing availability; does not create a reservation. |
| `/register/` | `GET`, `POST` | None | Registration form data on `POST` | Displays registration form; creates a user, logs the user in, and redirects home on success. |
| `/login/` | `GET`, `POST` | None | Login form data on `POST` | Displays login form; stores the user's login in the session and redirects home on success. |
| `/logout/` | `POST` | None | None | Removes the logged-in user from the session and redirects home. |

Passwords are stored with Django password hashing. The session stores a
logged-in user's unique `login`, which is used to retrieve the user for a
reservation.

## User interface

The application uses Django templates for page structure and an external
static CSS file for presentation. The shared base template loads the stylesheet
and provides a responsive viewport; the CSS keeps the navigation and forms
readable on desktop and mobile screens.

The shared navigation shows the Reservations link only for logged-in users.
`reservations.html` extends the base template and renders the logged-in user's
reservations, or an empty-state message when they have none.

The reservation form uses HTMX for one progressive-enhancement interaction.
Changing the guest count, date, or timeslot sends a `POST` request to
`/availability/`, which returns an HTML fragment for `#availability-result`.
The fragment is rendered from `availability_result.html` and reports input
guidance, validation errors, availability, a nearby available timeslot, or a
fully booked day. The normal form `POST` to `/reservations/` remains the only
operation that creates a reservation. The base template loads `htmx.min.js`
and sets the `X-CSRFToken` header for HTMX requests.

## Database

The project uses Django ORM with SQLite for local development. In Render
production, `DATABASE_URL` configures a Render PostgreSQL database.

## Deployment

The production deployment uses a Render Web Service with Waitress as the WSGI
application server. WhiteNoise serves collected static files. Render provides
`RENDER` and `RENDER_EXTERNAL_HOSTNAME`; the application uses them to disable
debug mode and configure allowed hosts. `SECRET_KEY` and `DATABASE_URL` are
managed as Render environment variables.

The application has no uploaded files or images, so media-file storage is not
configured.

## Models

### User

`User` stores a user's name, login, and password.

- `name`: user name
- `login`: unique login name
- `password`: password value

### RestaurantTable

`RestaurantTable` stores the tables in the restaurant.

- `number`: unique table number
- `capacity`: number of seats

### Reservation

`Reservation` stores a table reservation.

- `user`: user who made the reservation
- `table`: reserved restaurant table
- `guest_count`: number of guests
- `date`: reservation date
- `start_time`: reservation start time
- `end_time`: reservation end time
- `status`: `pending`, `confirmed`, or `cancelled`

Reservations created through the reservation form have the `confirmed` status.

## Relationships

- One user can have many reservations.
- One table can have many reservations.
- A reservation belongs to one user and one table.

## String representation

Each model has a `__str__()` method for readable output in the Django admin.

## Migrations

The initial database schema is stored in
`RestaurantApp/migrations/0001_initial.py`. The data migration
`RestaurantApp/migrations/0002_create_initial_restaurant_tables.py` creates 20
restaurant tables: four each with capacities 2, 4, 6, 8, and 10.
