from django.db import models
from patients.models import Patient
from accounts.models import Doctor
from appointment.models import Appointment
from django.utils.translation import gettext_lazy as _
# Create your models here.

class ClinicalExam(models.Model):
    """
    جلسة فحص سريري لمريض معيّن، تشمل الشكوى والنصيحة وربط الإجراءات
    """

    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name="clinical_exams")
    doctor = models.ForeignKey(Doctor, on_delete=models.SET_NULL, null=True)
    appointment = models.OneToOneField(Appointment, on_delete=models.SET_NULL, null=True, blank=True, related_name='clinical_exam')

    complaint = models.TextField(blank=True, null=True)
    medical_advice = models.TextField(blank=True, null=True)
    
    planned_procedures = models.ForeignKey(
    'DentalProcedure',
    on_delete=models.SET_NULL,
    null=True,
    blank=True,
    related_name='planned_exams'
)
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        verbose_name = _("Clinical Exam")
        verbose_name_plural = _("Clinical Exams")
        ordering = ["-created_at"]
        
    def __str__(self):
        return f"Exam for {self.patient} on {self.created_at.date()}"


# =========================
# قاموس الإجراءات (تعريفي)
# =========================
class DentalProcedure(models.Model):
    category = models.ForeignKey('ProcedureCategory', on_delete=models.SET_NULL, null=True, blank=True, related_name='procedures')
    name = models.CharField(max_length=150, unique=True, db_index=True)
    description = models.TextField(blank=True, null=True)
    default_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = _("Dental Procedure (Definition)")
        verbose_name_plural = _("Dental Procedures (Definitions)")
        ordering = ["name"]

    def __str__(self):
        return self.name


# =========================
# تصنيف الإجراءات
# =========================
class ProcedureCategory(models.Model):
    name = models.CharField(max_length=255, unique=True, db_index=True)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


# =========================
# قاموس الأسنان (FDI)
# =========================
class Toothcode(models.Model):
    class ToothType(models.TextChoices):
        PERMANENT = "permanent", _("Permanent")
        PRIMARY = "primary", _("Primary")

    tooth_number = models.CharField(max_length=10, db_index=True)  # مثل 11..48 أو 51..85
    tooth_type = models.CharField(max_length=10, choices=ToothType.choices, default=ToothType.PERMANENT)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = [("tooth_number", "tooth_type")]
        indexes = [models.Index(fields=["tooth_number", "tooth_type"])]
        ordering = ["tooth_type", "tooth_number"]

    def __str__(self):
        return f"{self.tooth_number} ({self.tooth_type})"


# =========================
# إجراء منفّذ لفحص سريري
# =========================
class Procedure(models.Model):
    """
    سجل تنفيذ لإجراء محدد ضمن فحص سريري.
    - definition: يشير للقاموس (اختياري)
    - name/description/cost: قيم قابلة للتعديل عند التنفيذ (تُنسخ من القاموس تلقائيًا إذا لم تُرسل)
    """
    clinical_exam = models.ForeignKey(ClinicalExam, on_delete=models.CASCADE, related_name="procedures")
    definition = models.ForeignKey(DentalProcedure, on_delete=models.PROTECT, null=True, blank=True, related_name="performed")
    category = models.ForeignKey(ProcedureCategory, on_delete=models.SET_NULL, null=True, blank=True, related_name="performed_procedures")

    name = models.CharField(max_length=255)  # يُملأ تلقائيًا من definition إذا لم يرسل
    description = models.TextField(blank=True, null=True)
    cost = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)

    status = models.CharField(max_length=30, blank=True, null=True)  # completed/in_progress/cancelled...
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [models.Index(fields=["clinical_exam"]), models.Index(fields=["created_at"])]
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.name} for {self.clinical_exam.patient} on {self.created_at.date()}"


# =============================
# الربط: إجراء منفّذ × أسنان
# =============================
class ProcedureToothcode(models.Model):
    procedure = models.ForeignKey(Procedure, on_delete=models.CASCADE, related_name="tooth_links")
    toothcode = models.ForeignKey(Toothcode, on_delete=models.PROTECT, related_name="procedure_links")
    performed_by = models.ForeignKey(Doctor, on_delete=models.SET_NULL, null=True, blank=True)
    notes = models.TextField(blank=True, null=True)
    performed_at = models.DateTimeField(auto_now_add=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = [("procedure", "toothcode")]
        indexes = [models.Index(fields=["procedure"]), models.Index(fields=["toothcode"])]
        ordering = ["-performed_at"]

    def __str__(self):
        return f"{self.procedure.name} - {self.toothcode.tooth_number}"
