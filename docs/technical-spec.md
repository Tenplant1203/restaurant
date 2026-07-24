# Technical Specification

## Application API

The application provides forms for registration, login, and reservation
creation.

| URL | Method | URL arguments | Request parameters | Response |
| --- | --- | --- | --- | --- |
| `/` | `GET` | None | None | HTML home page with the reservation form. |
| `/tables/` | `GET` | None | None | Plain-text list of restaurant tables, or a message when no tables exist. |
| `/reservations/` | `GET` | None | None | Plain-text list of reservations, or a message when no reservations exist. |
| `/reservations/` | `POST` | None | Reservation form data | Creates a confirmed reservation or redisplays the form with an error or alternative timeslot. |
| `/register/` | `GET`, `POST` | None | Registration form data on `POST` | Displays registration form; creates a user, logs the user in, and redirects home on success. |
| `/login/` | `GET`, `POST` | None | Login form data on `POST` | Displays login form; stores the user's login in the session and redirects home on success. |
| `/logout/` | `POST` | None | None | Removes the logged-in user from the session and redirects home. |

Passwords are stored with Django password hashing. The session stores a
logged-in user's unique `login`, which is used to retrieve the user for a
reservation.

## Database

The project uses Django ORM with SQLite for local development.

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

## Migration

The initial database schema is stored in
`RestaurantApp/migrations/0001_initial.py`.
