# Technical Specification

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

New reservations have the `pending` status.

## Relationships

- One user can have many reservations.
- One table can have many reservations.
- A reservation belongs to one user and one table.

## String representation

Each model has a `__str__()` method for readable output in the Django admin.

## Migration

The initial database schema is stored in
`RestaurantApp/migrations/0001_initial.py`.
