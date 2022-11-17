# DB_PROJ

PostgreSQL Account: aea2185

URL: http://34.148.138.206:8111/

Description of Implementation:

We were able to successfully implement the lookup and booking flight component from our original plan. We also implemented a manage functionality and admin functionality. In admin, we streamlined adding/deleting database entries such as airport, flight, pilot, and airplanes. Adding/Deleting data through admin page will automatically add/delete data in other tables that references it. Our manage page is where passengers can lookup their flight's information with their confirmation number and ID. From there, we allow passengers to modify their flight, that is, cancel it or change seats. We did not have time to separate flights into one-way or round-trip flights. We also opted to hard code flight data into our site, instead of fetching real-time data, to minimize the complexity of our implementation.


Description of Two Webpages:

The webpage we found the most interesting in terms of database operations is the manage page. Modifying an existing booking performs one of two functionalities. If the user chooses to change their seat by clicking on a new seat, then the server sends an UPDATE query to our database, editing the seating attribute. On the other hand, if the passenger cancels the booking, this will create three DELETE queries to remove the booking from booking, booked_on, and booked_by. Additionally, the passenger count for the flight is decremented by 1.

The second webpage we found interesting was the booking page, where passengers can book their flight. First the user inputs their personal information with their desired origin and destination along with the takeoff date. This translates to a SELECT query that matches the criteria of the search. If there are flights with the attributes specified by the user, then the user can click the book button to book the flight. This translates to an INSERT into booking, passenger, booked_on, and booked_by. Addtionally, we UPDATE the flight entity's passenger count by 1.

*Note that in both pages, although we chose to manually update capacity on book/cancel, we did not choose to manually change available/remaining seats as that information is pulled from the booking table everytime that it is called/needed
