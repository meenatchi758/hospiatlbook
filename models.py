from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

db = SQLAlchemy()

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(10), nullable=False)  # "patient" or "doctor"
    specialization = db.Column(db.String(100))  # only for doctors

class Appointment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    date = db.Column(db.String(20), nullable=False)
    time = db.Column(db.String(20), nullable=False)
    reason = db.Column(db.String(300), nullable=False)
    status = db.Column(db.String(50), default="Pending")

    # Relationships
    patient = db.relationship('User', foreign_keys=[patient_id], backref='appointments_patient')
    doctor = db.relationship('User', foreign_keys=[doctor_id], backref='appointments_doctor')

