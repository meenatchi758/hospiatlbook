from flask import Flask, render_template, redirect, url_for, flash, request
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, User, Appointment
from forms import LoginForm, AppointmentForm

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///clinic.db'
db.init_app(app)

login_manager = LoginManager()
login_manager.login_view = "login"
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Initialize DB and default doctor
def init_db():
    with app.app_context():
        db.create_all()
        if not User.query.filter_by(username="doctor1").first():
            doctor = User(
                username="Priya",
                password=generate_password_hash("doctor123"),
                is_doctor=True,
                specialization="Cardiologist"
            )
            db.session.add(doctor)
            db.session.commit()

# Home Page
@app.route("/")
def index():
    return render_template("index.html")

# Patient Booking
@app.route("/book", methods=["GET", "POST"])
def book_appointment():
    form = AppointmentForm()
    doctor = User.query.filter_by(is_doctor=True).first()
    if form.validate_on_submit():
        appointment = Appointment(
            patient_name=form.patient_name.data,
            patient_email=form.patient_email.data,
            doctor_id=doctor.id,
            date=form.date.data,
            time=form.time.data
        )
        db.session.add(appointment)
        db.session.commit()
        flash("Appointment booked successfully!", "success")
        return redirect(url_for("index"))
    return render_template("book_appointment.html", form=form, doctor=doctor)

# Doctor Dashboard
@app.route("/doctor")
@login_required
def doctor_dashboard():
    if not current_user.is_doctor:
        flash("Access denied", "danger")
        return redirect(url_for("index"))
    appointments = Appointment.query.filter_by(doctor_id=current_user.id).all()
    return render_template("doctor_dashboard.html", appointments=appointments)

# Update Appointment Status
@app.route("/update_status/<int:appt_id>", methods=["POST"])
@login_required
def update_status(appt_id):
    if not current_user.is_doctor:
        flash("Access denied", "danger")
        return redirect(url_for("index"))
    appt = Appointment.query.get_or_404(appt_id)
    appt.status = request.form.get("status")
    db.session.commit()
    flash(f"Appointment status updated to {appt.status}", "success")
    return redirect(url_for("doctor_dashboard"))

# Send Reminder
@app.route("/send_reminder/<int:appt_id>", methods=["POST"])
@login_required
def send_reminder(appt_id):
    if not current_user.is_doctor:
        flash("Access denied", "danger")
        return redirect(url_for("index"))
    appt = Appointment.query.get_or_404(appt_id)
    if not appt.reminder_sent:
        appt.reminder_sent = True
        db.session.commit()
        flash(f"Reminder sent to {appt.patient_email}", "success")
    else:
        flash("Reminder already sent", "info")
    return redirect(url_for("doctor_dashboard"))

# Login
@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and check_password_hash(user.password, form.password.data):
            login_user(user)
            return redirect(url_for("doctor_dashboard") if user.is_doctor else url_for("index"))
        flash("Invalid credentials", "danger")
    return render_template("login.html", form=form)

# Logout
@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("index"))

if __name__ == "__main__":
    init_db()
    app.run(debug=True)
