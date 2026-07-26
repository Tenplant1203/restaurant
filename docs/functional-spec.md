## Project Title

Fancy Restaurant

## Short Description

This app allows the user to book a table in a restaurant.

## Main User Actions

1. Enter the number of guests.
2. Choose a desired date in the calendar.
3. Choose a desired timeslot.
4. Enter a name and confirm the booking with an OK button.

## Basic Data Model Idea

- User
- Restaurant Table
- Reservation

## Note on the user interface

- The main page shows several input fields.
- If reservation for the desired timeslot is not available,
  the system suggests the closest available timeslot on the given day, or notifies the user that the day is completely booked.
- If the user books a table successfully, the system shows a success message.
- The user has to input a unique combination of login/password.
- If the user is logged in, there is no need to ask for the user name again.

## Reservation rules

- Reservations are available in one-hour timeslots from 11:00 to 21:00.
- A reservation must be for one or more guests and within the next 14 days.
- The system assigns the smallest available table that can accommodate the party.
- If the requested timeslot is unavailable, the system suggests the closest
  available timeslot on the same day. If the day is fully booked, it displays
  a full-booked message.
- When the user changes the guest count, date, or timeslot, the reservation
  form updates the availability message without reloading the page. The
  message indicates availability, suggests a nearby timeslot, or reports that
  the selected day is fully booked.
- Registered users can log in. Their name is populated from the session and
  cannot be changed in the reservation form. Guests enter a name for each
  reservation.
- Logged-in users can open the Reservations page to view only their own
  reservations. Users who are not logged in are directed to the login page.
