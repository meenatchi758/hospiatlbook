from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Email

class LoginForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    password = StringField("Password", validators=[DataRequired()])
    submit = SubmitField("Login")

class AppointmentForm(FlaskForm):
    patient_name = StringField("Your Name", validators=[DataRequired()])
    patient_email = StringField("Email", validators=[DataRequired(), Email()])
    date = StringField("Date (YYYY-MM-DD)", validators=[DataRequired()])
    time = StringField("Time (HH:MM)", validators=[DataRequired()])
    submit = SubmitField("Book Appointment")
