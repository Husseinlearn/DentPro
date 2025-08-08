from django.contrib import admin
from .models import (
    MedicalRecord,
    ChronicDisease,
    Attachment,
    Medication,
    PrescribedMedication
)
from patients.models import Patient
from appointment.models import Appointment
from procedures.models import ClinicalExam
from django.utils.html import format_html



# 🔹 عرض الأمراض المزمنة داخل السجل الطبي
class ChronicDiseaseInline(admin.TabularInline):
    model = ChronicDisease
    extra = 0


# 🔹 عرض المرفقات داخل السجل الطبي
class AttachmentInline(admin.TabularInline):
    model = Attachment
    extra = 0


@admin.register(MedicalRecord)
class MedicalRecordAdmin(admin.ModelAdmin):
    list_display = ['patient', 'created_at']
    readonly_fields = ['created_at', 'updated_at', 'patient_details', 'appointment_history']
    fields = ['patient', 'patient_details', 'appointment_history', 'created_at', 'updated_at']
    inlines = [ChronicDiseaseInline, AttachmentInline]

    def patient_details(self, obj):
        if not obj.patient:
            return "-"
        p = obj.patient
        return format_html(
            "الاسم: {} {}<br>"
            "البريد: {}<br>"
            "الجنس: {}<br>"
            "الجوال: {}<br>"
            "العنوان: {}<br>"
            "تاريخ الميلاد: {}",
            p.first_name, p.last_name,
            p.email or '---',
            p.gender,
            p.phone or '---',
            p.address or '---',
            p.date_of_birth
        )

    patient_details.short_description = "تفاصيل المريض"

    def appointment_history(self, obj):
        if not obj or not obj.patient:
            return "لا يوجد مريض مرتبط"

        patient = obj.patient
        appointments = Appointment.objects.filter(patient=patient).select_related('doctor__user', 'clinical_exam')

        if not appointments.exists():
            return "لا توجد مواعيد"

        rows = []
        for appt in appointments:
            row = f"<b>📅 التاريخ:</b> {appt.date} - <b>🕒 الوقت:</b> {appt.time}<br>"
            row += f"<b>👨‍⚕️ الطبيب:</b> {appt.doctor.user.get_full_name()}<br>"
            row += f"<b>📌 الحالة:</b> {appt.get_status_display()}<br>"

            exam = getattr(appt, 'clinical_exam', None)
            if exam:
                row += "<i>🔍 فحص سريري:</i><br>"
                row += f"&nbsp;&nbsp;- الشكوى: {exam.complaint or '-'}<br>"
                row += f"&nbsp;&nbsp;- النصيحة: {exam.medical_advice or '-'}<br>"
                row += f"&nbsp;&nbsp;- الإجراءات: {exam.planned_procedures or '-'}<br>"
            else:
                row += "<i>⚠ لا يوجد فحص سريري لهذا الموعد</i><br>"

            rows.append(row)

        return format_html("<hr>".join(rows))

    appointment_history.short_description = "سجل المواعيد والفحوصات"




@admin.register(ChronicDisease)
class ChronicDiseaseAdmin(admin.ModelAdmin):
    list_display = ['disease_name', 'medical_record', 'diagnosed_at']
    search_fields = ['disease_name', 'medical_record__patient__first_name', 'medical_record__patient__last_name']
    list_filter = ['diagnosed_at']


@admin.register(Attachment)
class AttachmentAdmin(admin.ModelAdmin):
    list_display = ['type', 'medical_record', 'uploaded_at']
    search_fields = ['medical_record__patient__first_name', 'medical_record__patient__last_name']
    list_filter = ['type', 'uploaded_at']
    raw_id_fields = ['medical_record']


@admin.register(Medication)
class MedicationAdmin(admin.ModelAdmin):
    list_display = ['name', 'default_dose_unit', 'is_active']
    search_fields = ['name']
    list_filter = ['is_active']


@admin.register(PrescribedMedication)
class PrescribedMedicationAdmin(admin.ModelAdmin):
    list_display = ['medication', 'clinical_exam', 'times_per_day', 'dose_unit', 'number_of_days', 'prescribed_by', 'prescribed_at']
    search_fields = ['medication__name', 'clinical_exam__patient__first_name', 'clinical_exam__patient__last_name']
    list_filter = ['prescribed_by', 'prescribed_at']
    raw_id_fields = ['clinical_exam', 'medication', 'prescribed_by']
