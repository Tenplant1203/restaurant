# Exercise 2: Project Proposal Sketch

## Main data entities

what kinds of objects or tables will the system need?

- User
- RestaurantTable
- Reservation

## Main user flow

Main user actions (ex01): what can the user do in the system?
Main user flow (ex02): how does the user interact with the system?

1. Input data of a reservation (the number of guests, desired date, desired timeslot)
   If the user is logged in, the system use username registered
   If the user isn't logged in, the system requires input of username
2. If the user pushed button, the system checks situation of tables
3. If there is a available table, the system assign suitable (by input data) reservation
4. If there is no a available table in given timeslot, the system suggest the closest available timeslot on the given day
5. If there is no a available table in all day, the system suggest the closest available timeslot on the near day
6. Finally, if the reservation is success, the system shows a success message.
