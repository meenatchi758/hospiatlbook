from flask import Flask, render_template, redirect, url_for, request, flash
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from datetime import datetime, timedelta

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secretkey'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///clinic.db'
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# -------------------- MODELS --------------------

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # 'patient' or 'doctor'
    specialization = db.Column(db.String(100))

class Appointment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    date = db.Column(db.String(20), nullable=False)
    time = db.Column(db.String(20), nullable=False)
    reason = db.Column(db.String(300), nullable=False)
    status = db.Column(db.String(50), default="Pending")
    reminder_sent = db.Column(db.Boolean, default=False)

    patient = db.relationship('User', foreign_keys=[patient_id], backref='patient_appointments')
    doctor = db.relationship('User', foreign_keys=[doctor_id], backref='doctor_appointments')

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# -------------------- ROUTES --------------------

@app.route('/')
def home():
    return render_template('index.html')

# ----------- AUTH -----------

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = bcrypt.generate_password_hash(request.form['password']).decode('utf-8')
        role = request.form['role']
        specialization = request.form.get('specialization')
        user = User(username=username, email=email, password=password, role=role, specialization=specialization)
        db.session.add(user)
        db.session.commit()
        flash("Registered Successfully!", "success")
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()
        if user and bcrypt.check_password_hash(user.password, password):
            login_user(user)
            if user.role == 'patient':
                return redirect(url_for('dashboard_patient'))
            else:
                return redirect(url_for('dashboard_doctor'))
        flash("Invalid credentials", "danger")
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))

# ----------- PATIENT DASHBOARD -----------

@app.route('/dashboard/patient')
@login_required
def dashboard_patient():
    if current_user.role != 'patient':
        return redirect(url_for('home'))
    appointments = Appointment.query.filter_by(patient_id=current_user.id).all()
    return render_template('dashboard_patient.html', appointments=appointments)

# ----------- DOCTOR DASHBOARD -----------

@app.route('/dashboard/doctor')
@login_required
def dashboard_doctor():
    if current_user.role != 'doctor':
        return redirect(url_for('home'))
    appointments = Appointment.query.filter_by(doctor_id=current_user.id).all()
    return render_template('dashboard_doctor.html', appointments=appointments)

@app.route('/approve/<int:id>')
@login_required
def approve(id):
    appt = Appointment.query.get_or_404(id)
    if current_user.role == 'doctor':
        appt.status = "Approved"
        db.session.commit()
        flash("Appointment Approved!", "success")
    return redirect(url_for('dashboard_doctor'))

@app.route('/reject/<int:id>')
@login_required
def reject(id):
    appt = Appointment.query.get_or_404(id)
    if current_user.role == 'doctor':
        appt.status = "Rejected"
        db.session.commit()
        flash("Appointment Rejected!", "danger")
    return redirect(url_for('dashboard_doctor'))

# ----------- BOOK APPOINTMENT -----------

@app.route('/book', methods=['GET', 'POST'])
@login_required
def book_appointment():
    if current_user.role != 'patient':
        return redirect(url_for('home'))

    doctors = User.query.filter_by(role='doctor').limit(4).all()

    if request.method == 'POST':
        doctor_id = request.form['doctor_id']
        date = request.form['date']
        time = request.form['time']
        reason = request.form['reason']

        appt = Appointment(patient_id=current_user.id, doctor_id=doctor_id, date=date, time=time, reason=reason)
        db.session.add(appt)
        db.session.commit()
        flash("Appointment booked successfully!", "success")
        return redirect(url_for('dashboard_patient'))

    return render_template('book_appointment.html', doctors=doctors)

# ----------- REMINDER SYSTEM -----------

@app.route('/send_reminders')
def send_reminders():
    now = datetime.now()
    appointments = Appointment.query.filter_by(status='Approved', reminder_sent=False).all()
    for appt in appointments:
        appt_datetime = datetime.strptime(f"{appt.date} {appt.time}", "%Y-%m-%d %H:%M")
        if 0 <= (appt_datetime - now).total_seconds() <= 86400:  # within 24 hours
            print(f"Reminder: Appointment for {appt.patient.username} with {appt.doctor.username} at {appt.time} on {appt.date}")
            appt.reminder_sent = True
    db.session.commit()
    return "Reminders processed successfully!"

# -------------------- INITIAL SETUP --------------------

if __name__ == '__main__':
    with app.app_context():
        db.create_all()

        if not User.query.filter_by(role='doctor').first():
            doctors = [
                ("Dr. Smith", "smith@clinic.com", "Cardiologist"),
                ("Dr. Johnson", "johnson@clinic.com", "Dermatologist"),
                ("Dr. Brown", "brown@clinic.com", "Pediatrician"),
                ("Dr. Taylor", "taylor@clinic.com", "Orthopedic"),
            ]
            for name, email, spec in doctors:
                pwd = bcrypt.generate_password_hash("password").decode('utf-8')
                db.session.add(User(username=name, email=email, password=pwd, role="doctor", specialization=spec))
            db.session.commit()

    app.run(debug=True)
