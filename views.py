from django.shortcuts import render, redirect
from .models import Doctor, Appointment
import random

def book_appointment(request):
    # Get all doctors
    all_doctors = list(Doctor.objects.all())
    # Pick 4 random doctors
    doctors = random.sample(all_doctors, min(len(all_doctors), 4))

    if request.method == "POST":
        doctor_id = request.POST.get("doctor_id")
        date = request.POST.get("date")
        time = request.POST.get("time")
        reason = request.POST.get("reason")

        doctor = Doctor.objects.get(id=doctor_id)
        # Create appointment
        Appointment.objects.create(
            patient=request.user.patient,
            doctor=doctor,
            date=date,
            time=time,
            reason=reason
        )
        return redirect("dashboard_patient")

    return render(request, "book_appointment.html", {"doctors": doctors})
