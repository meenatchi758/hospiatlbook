from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField, DateTimeField
from wtforms.validators import DataRequired, Email, Length

class RegisterForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired(), Length(min=6)])
    role = SelectField("Role", choices=[("patient", "Patient"), ("doctor", "Doctor")])
    specialization = StringField("Specialization")  # only for doctors
    submit = SubmitField("Register")

class LoginForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Login")

class AppointmentForm(FlaskForm):
    doctor_id = SelectField("Select Doctor", coerce=int)
    date_time = DateTimeField("Date & Time (YYYY-MM-DD HH:MM)", validators=[DataRequired()])
    submit = SubmitField("Book Appointment")
