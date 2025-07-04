from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_socketio import SocketIO
from flask_cors import CORS
from dotenv import load_dotenv
import os
from datetime import datetime

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your-secret-key')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///smart_delivery.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
socketio = SocketIO(app, cors_allowed_origins="*")
CORS(app)

# Import models and routes
from backend.app.models.delivery import Delivery, Vehicle, Route
from backend.app.routes.delivery_routes import delivery_routes
from backend.app.routes.vehicle_routes import vehicle_routes
from backend.app.routes.route_optimizer import route_optimizer_routes

# Register blueprints
app.register_blueprint(delivery_routes)
app.register_blueprint(vehicle_routes)
app.register_blueprint(route_optimizer)

@app.route('/')
def index():
    return jsonify({
        'status': 'success',
        'message': 'Smart Delivery Route Optimization API is running'
    })

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=5000, debug=True)
