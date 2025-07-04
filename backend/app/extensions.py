from flask_sqlalchemy import SQLAlchemy
from flask_socketio import SocketIO
from flask_cors import CORS

# Database instance
db = SQLAlchemy()

# SocketIO instance
socketio = SocketIO()

# CORS instance
cors = CORS()
