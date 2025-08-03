from django.db import models
from patients.models import Patient
from accounts.models import Doctor
from appointment.models import Appointment
# Create your models here.

class ClinicalExam(models.Model):
    """
    جلسة فحص سريري لمريض معيّن، تشمل الشكوى والنصيحة وربط الإجراءات
    """

    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name="clinical_exams")
    doctor = models.ForeignKey(Doctor, on_delete=models.SET_NULL, null=True)
    appointment = models.ForeignKey(Appointment, on_delete=models.SET_NULL, null=True, blank=True)

    complaint = models.TextField(blank=True, null=True)
    medical_advice = models.TextField(blank=True, null=True)
    planned_procedures = models.TextField(blank=True, null=True)


    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Exam for {self.patient} on {self.created_at.date()}"


