from flask import Flask, render_template, request, redirect, jsonify, flash, session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timezone
from utils.geocoding import get_lat_lon
from algorithms import Graph
import math
import logging
import osmnx as ox
import json
import networkx as nx

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.secret_key = 'secret-key'  # Required for flash messages
# @app.route('/get-coordinates', methods=['POST'])
# def get_coordinates():
#     data = request.get_json()
#     locations = data.get('locations', [])
    
#     results = {}
#     for loc in locations:
#         lat, lon = get_lat_lon(loc)
#         if lat and lon:ṣ
#             results[loc] = {'lat': lat, 'lon': lon}
#         else:
#             results[loc] = None  # or handle errors as needed
    
#     return jsonify(results)

app.config['SQLALCHEMY_DATABASE_URI']="sqlite:///Smart.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=False
db=SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    routes = db.relationship('SmartOptimizer', backref='user', lazy=True)
    date_created = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    def __repr__(self):
        return f"User {self.name}"

class SmartOptimizer(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    Source = db.Column(db.String(100), nullable=False)
    Destinations = db.Column(db.String(100), nullable=False)
    date_created = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)

    def __repr__(self)-> str:
        return f"{self.Source}-{self.Destinations}"

    def get_formatted_date(self):
        # Convert UTC to local time (IST is UTC+5:30)
        local_time = self.date_created.replace(tzinfo=timezone.utc).astimezone()
        return local_time.strftime('%Y-%m-%d %H:%M:%S')

    def to_dict(self):
        return {
            'sno': self.sno,
            'source': self.Source,
            'destination': self.Destinations,
            'date_created': self.get_formatted_date(),
            'user_id': self.user_id
        }

with app.app_context():
    db.create_all()
    

def calculate_distance(lat1, lon1, lat2, lon2):
    """Calculate the distance between two points using the Haversine formula."""
    try:
        R = 6371  # Earth's radius

        lat1, lon1, lat2, lon2 = map(math.radians, [float(lat1), float(lon1), float(lat2), float(lon2)])
        dlat = lat2 - lat1
        dlon = lon2 - lon1

        a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
        c = 2 * math.asin(math.sqrt(a))
        distance = R * c

        return round(distance, 2)
    except Exception as e:
        logger.error(f"Error calculating distance: {str(e)}")
        return None

def create_graph(source, destination):
    """Create a graph with the source, destination, and intermediate nodes."""
    try:
        g = Graph()
        
        source_lat, source_lon = get_lat_lon(source)
        dest_lat, dest_lon = get_lat_lon(destination)
        
        if not all([source_lat, source_lon, dest_lat, dest_lon]):
            logger.error(f"Could not get coordinates for locations: {source} or {destination}")
            return None
        
        g.add_coordinate('source', source_lat, source_lon)
        g.add_coordinate('destination', dest_lat, dest_lon)
        
        intermediate_points = {
            'Bijnor': (29.3721, 78.1363),
            'Moradabad': (28.8388, 78.7738),
            'Rampur': (28.8029, 79.0250),
            'Bareilly': (28.3670, 79.4304),
            'Haldwani': (29.2208, 79.5286)
        }
        
        for city, (lat, lon) in intermediate_points.items():
            g.add_coordinate(city, lat, lon)
        
        points = ['source'] + list(intermediate_points.keys()) + ['destination']
        
        for i in range(len(points)):
            for j in range(i + 1, len(points)):
                point1 = points[i]
                point2 = points[j]
                
                if point1 == 'source':
                    lat1, lon1 = source_lat, source_lon
                elif point1 == 'destination':
                    lat1, lon1 = dest_lat, dest_lon
                else:
                    lat1, lon1 = intermediate_points[point1]
                
                if point2 == 'source':
                    lat2, lon2 = source_lat, source_lon
                elif point2 == 'destination':
                    lat2, lon2 = dest_lat, dest_lon
                else:
                    lat2, lon2 = intermediate_points[point2]
                
                # Calculate distance between points
                distance = calculate_distance(lat1, lon1, lat2, lon2)
                if distance is not None:
                    g.add_edge(point1, point2, distance)
        
        return g
    except Exception as e:
        logger.error(f"Error creating graph: {str(e)}")
        return None

@app.route("/")
def hello_world():
    return render_template('index.html')

@app.route("/admin_panel")
def admin_panel():
    try:
        total_users = 1 
        total_routes = SmartOptimizer.query.count()
        total_destinations = len(set(route.Destinations for route in SmartOptimizer.query.all()))
        
        users = [{'id': 1, 'name': 'Admin', 'email': 'admin@example.com', 'route_count': total_routes}]
        
        return render_template('admin_panel.html', 
                             total_users=total_users,
                             total_routes=total_routes,
                             total_destinations=total_destinations,
                             users=users)
    except Exception as e:
        logger.error(f"Error loading admin panel: {str(e)}")
        flash("Error loading admin panel", "error")
        return redirect("/")

@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        logger.info(f"Login attempt - Email: {email}")
        
        if not email or not password:
            flash('Please enter both email and password', 'error')
            return render_template('login.html')
            
        try:
            user = User.query.filter_by(email=email).first()
            logger.info(f"User found: {user is not None}")
            
            if user and user.password == password:
                session['user_id'] = user.id
                session['user_name'] = user.name
                session['user_email'] = user.email
                logger.info(f"Login successful - User ID: {user.id}")
                flash('Login successful!', 'success')
                return redirect('/plan_routes')  # Redirecting- successful login
            else:
                logger.warning(f"Invalid login attempt for email: {email}")
                flash('Invalid email or password', 'error')
                return render_template('login.html')
        except Exception as e:
            logger.error(f"Error during login: {str(e)}")
            flash('An error occurred during login. Please try again.', 'error')
            return render_template('login.html')
            
    return render_template('login.html')

@app.route("/signup", methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        logger.info(f"Signup attempt - Email: {email}, Name: {name}")
        
        if not all([name, email, password, confirm_password]):
            flash('All fields are required', 'error')
            return render_template('signup.html')
            
        if password != confirm_password:
            flash('Passwords do not match', 'error')
            return render_template('signup.html')
            
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash('Email already registered', 'error')
            return render_template('signup.html')
            
        try:
            # Create new user
            new_user = User(name=name, email=email, password=password)
            db.session.add(new_user)
            db.session.commit()
            logger.info(f"User created successfully - ID: {new_user.id}")
            
            flash('Registration successful! Please login to continue.', 'success')
            return redirect('/login')
        except Exception as e:
            logger.error(f"Error creating user: {str(e)}")
            db.session.rollback()
            flash('Error creating account. Please try again.', 'error')
            return render_template('signup.html')
        
    return render_template('signup.html')

@app.route("/profile")
def profile():
    if 'user_id' not in session:
        flash('Please login to view your profile', 'error')
        return redirect('/login')
        
    user = User.query.get(session['user_id'])
    if not user:
        session.clear()
        flash('User not found', 'error')
        return redirect('/login')
        
    # Get user's routes
    user_routes = SmartOptimizer.query.filter_by(user_id=user.id).all()
    
    return render_template('profile.html', 
                         user=user,
                         routes=user_routes)

@app.route("/logout")
def logout():
    session.clear()
    flash('You have been logged out successfully.', 'success')
    return redirect('/')

@app.route("/plan_routes", methods=['GET', 'POST'])
def plan_routes():
    if 'user_id' not in session:
        flash('Please login to plan routes', 'error')
        return redirect('/login')
        
    if request.method=="POST":
        source = request.form.get('Source')
        destination = request.form.get('Destinations')
        
        if not source or not destination:
            flash("Both source and destination are required!", "error")
            return render_template('plan_routes.html', error="Both fields are required!")

        try:
            graph = create_graph(source, destination)
            if not graph:
                flash("Could not get coordinates for the locations. Please check the addresses.", "error")
                return render_template('plan_routes.html', error="Could not get coordinates for the locations!")

            dijkstra_cost, dijkstra_path = graph.dijkstra('source', 'destination')
            bellman_cost, bellman_path = graph.bellman_ford('source', 'destination')
            astar_cost, astar_path = graph.a_star('source', 'destination')

            obj = SmartOptimizer(
                Source=source, 
                Destinations=destination,
                user_id=session['user_id']
            )
            db.session.add(obj)
            db.session.commit()

            routes = {
                'dijkstra': {
                    'cost': round(dijkstra_cost, 2),
                    'path': dijkstra_path
                },
                'bellman': {
                    'cost': round(bellman_cost, 2),
                    'path': bellman_path
                },
                'astar': {
                    'cost': round(astar_cost, 2),
                    'path': astar_path
                }
            }

            avg_speed = 50  # km/h
            duration = round(max(dijkstra_cost, bellman_cost, astar_cost) / avg_speed, 1)

            flash("Route calculated successfully!", "success")
            return render_template('map.html', 
                                 success=True, 
                                 routes=routes,
                                 source=source,
                                 destination=destination,
                                 duration=f"{duration} hours")

        except Exception as e:
            logger.error(f"Error calculating route: {str(e)}")
            flash(f"An error occurred while calculating the route: {str(e)}", "error")
            return render_template('plan_routes.html', error="An error occurred while calculating the route!")

    return render_template('plan_routes.html')

@app.route("/saved_routes")
def saved_routes():
    if 'user_id' not in session:
        flash('Please login to view saved routes', 'error')
        return redirect('/login')
        
    try:
        allObj = SmartOptimizer.query.filter_by(user_id=session['user_id']).all()
        return render_template('saved_routes.html', allObj=allObj)
    except Exception as e:
        logger.error(f"Error fetching saved routes: {str(e)}")
        flash("Error loading saved routes", "error")
        return redirect("/")

@app.route("/smart_recommendations")
def smart_recommendations():
    return render_template('smart_recommendations.html')

@app.route("/delete/<int:sno>")
def delete(sno):
    try:
        obj=SmartOptimizer.query.filter_by(sno=sno).first()
        if obj:
            db.session.delete(obj)
            db.session.commit()
            flash("Route deleted successfully!", "success")
        else:
            flash("Route not found!", "error")
    except Exception as e:
        logger.error(f"Error deleting route: {str(e)}")
        flash("Error deleting route", "error")
    return redirect('/saved_routes')

@app.route("/update/<int:sno>", methods=['GET', 'POST'])
def update(sno):
    try:
        if request.method=='POST':
            source = request.form['Source']
            destination = request.form['Destinations']
            if source and destination:
                obj=SmartOptimizer.query.filter_by(sno=sno).first()
                if obj:
                    obj.Source=source
                    obj.Destinations=destination
                    db.session.add(obj)
                    db.session.commit()
                    flash("Route updated successfully!", "success")
                    return redirect('/saved_routes')
                else:
                    flash("Route not found!", "error")
                    return redirect('/saved_routes')
        obj=SmartOptimizer.query.filter_by(sno=sno).first()
        if obj:
            return render_template('update.html', obj=obj)
        else:
            flash("Route not found!", "error")
            return redirect('/saved_routes')
    except Exception as e:
        logger.error(f"Error updating route: {str(e)}")
        flash("Error updating route", "error")
        return redirect('/saved_routes')

def get_shortest_path(source_lat, source_lon, dest_lat, dest_lon):
    """
    Uses OSMnx and NetworkX to find the shortest path between two coordinates.
    Returns the list of node coordinates along the path and the total distance in km.
    """
    try:
        # Download the graph for the area between source and destination
        north = max(source_lat, dest_lat) + 0.01
        south = min(source_lat, dest_lat) - 0.01
        east = max(source_lon, dest_lon) + 0.01
        west = min(source_lon, dest_lon) - 0.01

        G = ox.graph_from_bbox(north, south, east, west, network_type='drive')
        orig_node = ox.nearest_nodes(G, source_lon, source_lat)
        dest_node = ox.nearest_nodes(G, dest_lon, dest_lat)

        path = nx.shortest_path(G, orig_node, dest_node, weight='length')
        distance = nx.shortest_path_length(G, orig_node, dest_node, weight='length') / 1000  # meters to km

        # Get coordinates for each node in the path
        path_nodes = [(G.nodes[n]['y'], G.nodes[n]['x']) for n in path]
        return path_nodes, distance
    except Exception as e:
        logger.error(f"Error in get_shortest_path: {str(e)}")
        return [], 0

@app.route("/view/<int:sno>")
@app.route("/view/<int:sno>")
# def view(sno):
#     try:
#         route = SmartOptimizer.query.filter_by(sno=sno).first()
#         if route:
#             source_lat, source_lon = get_lat_lon(route.Source)
#             dest_lat, dest_lon = get_lat_lon(route.Destinations)

#             if not all([source_lat, source_lon, dest_lat, dest_lon]):
#                 flash("Could not get coordinates for the locations", "error")
#                 return redirect('/saved_routes')

#             # Use Dijkstra here
#             path_nodes, distance = get_shortest_path(source_lat, source_lon, dest_lat, dest_lon)
#             duration = round(distance / 40, 2)  # assuming average speed of 40 km/h

#             return render_template('view_route.html',
#                                    route=route,
#                                    source_lat=source_lat,
#                                    source_lon=source_lon,
#                                    dest_lat=dest_lat,
#                                    dest_lon=dest_lon,
#                                    distance=round(distance, 2),
#                                    duration=duration,
#                                    path=path_nodes)
#         else:
#             flash("Route not found!", "error")
#             return redirect('/saved_routes')
#     except Exception as e:
#         logger.error(f"Error viewing route: {str(e)}")
#         flash("Error viewing route", "error")
#         return redirect('/saved_routes')


def view(sno):
    try:
        route = SmartOptimizer.query.filter_by(sno=sno).first()
        if route:
            # Get coordinates
            source_lat, source_lon = get_lat_lon(route.Source)
            dest_lat, dest_lon = get_lat_lon(route.Destinations)

            if not all([source_lat, source_lon, dest_lat, dest_lon]):
                flash("Could not get coordinates for the locations", "error")
                return redirect('/saved_routes')

            # Distance and duration
            distance = calculate_distance(source_lat, source_lon, dest_lat, dest_lon)
            if distance is None:
                flash("Error calculating distance", "error")
                return redirect('/saved_routes')

            duration = round(distance / 50, 1)  # Approximate time (hrs)

            # 💡 Generate path (just source → destination for now)
            # path = [(source_lat, source_lon), (dest_lat, dest_lon)]
            path, distance = get_shortest_path(source_lat, source_lon, dest_lat, dest_lon)

            path_json = json.dumps(path)

            return render_template('view_route.html',
                                   route=route,
                                   source_lat=source_lat,
                                   source_lon=source_lon,
                                   dest_lat=dest_lat,
                                   dest_lon=dest_lon,
                                   distance=distance,
                                   duration=duration,
                                   path=path,  # Pass the path for rendering
                                   path_json=path_json)  # ← Pass this
        else:
            flash("Route not found!", "error")
            return redirect('/saved_routes')

    except Exception as e:
        logger.error(f"Error viewing route: {str(e)}")
        flash("Error viewing route", "error")
        return redirect('/saved_routes')


@app.route('/save_route', methods=['POST'])
def save_route():
    if 'user_id' not in session:
        return jsonify({'success': False, 'error': 'User not logged in'}), 401
    
    try:
        data = request.get_json()
        source = data.get('source')
        destination = data.get('destination')
        
        if not all([source, destination]):
            return jsonify({'success': False, 'error': 'Missing required fields'}), 400
        
        new_route = SmartOptimizer( #Creating new route
            Source=source,
            Destinations=destination,
            user_id=session['user_id']
        )
        
        db.session.add(new_route)
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Route saved successfully'})
    except Exception as e:
        db.session.rollback()
        app.logger.error(f"Error saving route: {str(e)}")
        return jsonify({'success': False, 'error': 'Failed to save route'}), 500

if __name__ == '__main__':
    app.run(host='localhost', port=5000, debug=True)