# Route-Optimization
This is a Flask web application for Smart route planning and management. Users are able to register, log in, 
and design travel routes from city to city. The application uses geocoding to translate city names into coordinates 
and graph algorithms (Dijkstra, Bellman-Ford, A*) to determine optimal routes. Users can list, save, update, and 
delete planned routes, and all data is stored within a SQLite database through SQLAlchemy. The application also has an 
admin page for overview statistics and includes user authentication, session management, and interactive route 
visualization. 
->Presentation Layer (Frontend) 
o HTML templates rendered via Flask 
o User interfaces for login, signup, route 
planning, profile, admin panel, etc. 
o Flash messages for user feedback 
o CSS for Page design and style 
-> Application Layer (Flask Backend) 
o Handles HTTP requests, session 
management, and routing 
o Implements business logic for user 
authentication, route planning, and 
CRUD operations on routes 
-> Algorithm Layer 
o Contains graph algorithms (Dijkstra, 
Bellman-Ford, A*) for route optimization 
o Distance calculation using the Haversine 
formula 
  -> Data Layer 
o SQLAlchemy ORM models 
for user and smart optimization  
o SQLite database for persistent storage 
  -> Utility Layer 
o Geocoding utilities to fetch coordinates 
for city names
