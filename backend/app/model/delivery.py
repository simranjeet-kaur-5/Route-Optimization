from ..extensions import db
from datetime import datetime

class Delivery(db.Model):
    __tablename__ = 'deliveries'
    
    id = db.Column(db.Integer, primary_key=True)
    vehicle_id = db.Column(db.Integer, db.ForeignKey('vehicles.id'))
    address = db.Column(db.String(200), nullable=False)
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), default='pending')
    estimated_time = db.Column(db.DateTime)
    actual_time = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    vehicle = db.relationship('Vehicle', back_populates='deliveries')

class Vehicle(db.Model):
    __tablename__ = 'vehicles'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    capacity = db.Column(db.Integer, nullable=False)
    current_latitude = db.Column(db.Float)
    current_longitude = db.Column(db.Float)
    status = db.Column(db.String(20), default='available')
    last_update = db.Column(db.DateTime, default=datetime.utcnow)
    
    deliveries = db.relationship('Delivery', back_populates='vehicle')
    
    def update_location(self, latitude, longitude):
        self.current_latitude = latitude
        self.current_longitude = longitude
        self.last_update = datetime.utcnow()
        db.session.commit()

class Route(db.Model):
    __tablename__ = 'routes'
    
    id = db.Column(db.Integer, primary_key=True)
    vehicle_id = db.Column(db.Integer, db.ForeignKey('vehicles.id'))
    start_time = db.Column(db.DateTime, default=datetime.utcnow)
    end_time = db.Column(db.DateTime)
    total_distance = db.Column(db.Float)
    total_duration = db.Column(db.Integer)  # in seconds
    status = db.Column(db.String(20), default='planned')
    
    vehicle = db.relationship('Vehicle', back_populates='routes')
