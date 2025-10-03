from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

db = SQLAlchemy()

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    is_doctor = db.Column(db.Boolean, default=False)
    specialization = db.Column(db.String(100))  # Doctor specialization

class Appointment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    patient_name = db.Column(db.String(100), nullable=False)
    patient_email = db.Column(db.String(100), nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    doctor = db.relationship('User', backref='appointments')
    date = db.Column(db.String(20), nullable=False)
    time = db.Column(db.String(20), nullable=False)
    status = db.Column(db.String(20), default="Pending")
    reminder_sent = db.Column(db.Boolean, default=False)
