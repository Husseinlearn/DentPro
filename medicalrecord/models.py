from django.db import models
from django.utils.translation import gettext_lazy as _
from patients.models import Patient
from accounts.models import Doctor
from appointment.models import Appointment
# Create your models here.

class MedicalRecord(models.Model):
    """السجل الطبي الرئيسي لكل مريض"""
    
    patient = models.OneToOneField(Patient, on_delete=models.CASCADE, related_name='medical_record')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("Medical Record")
        verbose_name_plural = _("Medical Records")

    def __str__(self):
        return f"Medical Record - {self.patient}"


class ChronicDisease(models.Model):
    """الأمراض المزمنة المرتبطة بسجل المريض"""
    
    medical_record = models.ForeignKey(MedicalRecord, on_delete=models.CASCADE, related_name='chronic_diseases')
    disease_name = models.CharField(max_length=255)
    notes = models.TextField(blank=True, null=True)
    diagnosed_at = models.DateField(blank=True, null=True)

    class Meta:
        verbose_name = _("Chronic Disease")
        verbose_name_plural = _("Chronic Diseases")

    def __str__(self):
        return f"{self.disease_name} - {self.medical_record.patient}"


class Attachment(models.Model):
    """المرفقات المرتبطة بالسجل الطبي أو الفحوصات"""
    class AttachmentType(models.TextChoices):
        XRAY = "xray", _("X-Ray")
        REPORT = "report", _("Report")
        IMAGE = "image", _("Image")
        OTHER = "other", _("Other")

    
    medical_record = models.ForeignKey(MedicalRecord, on_delete=models.CASCADE, related_name='attachments')
    file = models.FileField(upload_to='medical_attachments/')
    type = models.CharField(max_length=20, choices=AttachmentType.choices, default=AttachmentType.OTHER)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    description = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name = _("Attachment")
        verbose_name_plural = _("Attachments")

    def __str__(self):
        return f"{self.get_type_display()} - {self.medical_record.patient}"

class Medication(models.Model):
    """تعريف دواء متاح في النظام"""
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True, null=True)
    default_dose_unit = models.CharField(max_length=50, blank=True, null=True)  # مثال: حبة، كبسولة
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name



class PrescribedMedication(models.Model):
    """
    وصفة طبية مرتبطة بدواء ,الفحص السريري 
    """
    clinical_exam = models.ForeignKey("procedures.ClinicalExam", on_delete=models.CASCADE, related_name="medications")
    medication = models.ForeignKey("Medication", on_delete=models.PROTECT, related_name="prescriptions")
    times_per_day = models.IntegerField()
    dose_unit = models.CharField(max_length=50)
    number_of_days = models.IntegerField()
    notes = models.TextField(blank=True, null=True)

    prescribed_by = models.ForeignKey("accounts.Doctor", on_delete=models.SET_NULL, null=True)
    prescribed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.medication.name} for {self.clinical_exam.patient}"


