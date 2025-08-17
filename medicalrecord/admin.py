from django.contrib import admin
from django.utils.html import format_html, format_html_join

from .models import (
    MedicalRecord,
    Attachment,
    Medication,
    PrescribedMedication,
    MedicationPackage,
    MedicationPackageItem,
    AppliedMedicationPackage,
)
from appointment.models import Appointment


# ===========================
# Inlines
# ===========================
class AttachmentInline(admin.TabularInline):
    model = Attachment
    extra = 0
    fields = ["file", "type", "description", "uploaded_at"]
    readonly_fields = ["uploaded_at"]


class MedicationPackageItemInline(admin.TabularInline):
    model = MedicationPackageItem
    extra = 1
    autocomplete_fields = ["medication"]
    fields = ["medication", "times_per_day", "dose_unit", "number_of_days", "notes"]


# ===========================
# MedicalRecord Admin
# ===========================
@admin.register(MedicalRecord)
class MedicalRecordAdmin(admin.ModelAdmin):
    list_display = ["patient", "created_at"]
    search_fields = ["patient__first_name", "patient__last_name", "patient__email"]
    readonly_fields = [
        "created_at", "updated_at",
        "patient_details",
        "patient_diseases_list",
        "patient_allergies_list",
        "appointment_history",
    ]
    fields = [
        "patient",
        "patient_details",
        "patient_diseases_list",
        "patient_allergies_list",
        "appointment_history",
        "created_at", "updated_at",
    ]
    inlines = [AttachmentInline]

    # --- تفاصيل المريض
    def patient_details(self, obj):
        if not obj or not obj.patient:
            return "-"
        p = obj.patient
        gender_display = getattr(p, "get_gender_display", None)
        gender_value = gender_display() if callable(gender_display) else (p.gender or "—")
        return format_html(
            "الاسم: {} {}<br>"
            "البريد: {}<br>"
            "الجنس: {}<br>"
            "الجوال: {}<br>"
            "العنوان: {}<br>"
            "تاريخ الميلاد: {}<br>"
            "المعرّف (UUID): {}",
            p.first_name or "—",
            p.last_name or "—",
            p.email or "—",
            gender_value,
            p.phone or "—",
            p.address or "—",
            getattr(p, "date_of_birth", "—") or "—",
            getattr(p, "id", "—"),
        )
    patient_details.short_description = "تفاصيل المريض"

    # --- الأمراض المزمنة (افترض related_name='patient_diseases')
    def patient_diseases_list(self, obj):
        if not obj or not obj.patient:
            return "لا يوجد مريض مرتبط"
        rel = getattr(obj.patient, "patient_diseases", None)
        if not rel:
            return "—"
        items = []
        for pd in rel.all():
            name = getattr(getattr(pd, "disease", None), "name", None) or getattr(pd, "disease_name", None) or "—"
            diagnosed = getattr(pd, "diagnosed_at", None) or "غير محدد"
            notes = getattr(pd, "notes", None) or ""
            items.append((f"{name} — {diagnosed} {('— '+notes) if notes else ''}",))
        return format_html_join("\n", "<div>• {}</div>", items) if items else "لا يوجد"
    patient_diseases_list.short_description = "الأمراض المزمنة"

    # --- حساسيّات الأدوية (افترض related_name='patient_allergies')
    # ملاحظة: نستعمل getattr لتفادي الأخطاء إن لم توجد الحقول
    def patient_allergies_list(self, obj):
        if not obj or not obj.patient:
            return "لا يوجد مريض مرتبط"
        rel = getattr(obj.patient, "patient_allergies", None)
        if not rel:
            return "—"
        items = []
        for pa in rel.all():
            med_name = getattr(getattr(pa, "medication", None), "name", None) or "—"
            severity = getattr(pa, "severity", None) or "—"
            notes = getattr(pa, "notes", None) or ""
            items.append((f"{med_name} — الشدة: {severity} {('— '+notes) if notes else ''}",))
        return format_html_join("\n", "<div>• {}</div>", items) if items else "لا يوجد"
    patient_allergies_list.short_description = "حساسيات الأدوية"

    # --- سجل المواعيد والفحوصات
    def appointment_history(self, obj):
        if not obj or not obj.patient:
            return "لا يوجد مريض مرتبط"
        appointments = (
            Appointment.objects
            .filter(patient=obj.patient)
            .select_related("doctor__user")
            .order_by("-date", "-time")
        )
        if not appointments.exists():
            return "لا توجد مواعيد"

        rows = []
        for appt in appointments:
            doctor_name = (
                appt.doctor.user.get_full_name()
                if getattr(appt, "doctor", None) and getattr(appt.doctor, "user", None)
                else "—"
            )
            status_display = appt.get_status_display() if hasattr(appt, "get_status_display") else (appt.status or "—")

            row = f"<b>📅 التاريخ:</b> {getattr(appt, 'date', '—')} - <b>🕒 الوقت:</b> {getattr(appt, 'time', '—')}<br>"
            row += f"<b>👨‍⚕️ الطبيب:</b> {doctor_name}<br>"
            row += f"<b>📌 الحالة:</b> {status_display}<br>"

            exam = getattr(appt, "clinical_exam", None)
            if exam:
                row += "<i>🔍 فحص سريري:</i><br>"
                row += f"&nbsp;&nbsp;- الشكوى: {getattr(exam, 'complaint', None) or '-'}<br>"
                row += f"&nbsp;&nbsp;- النصيحة: {getattr(exam, 'medical_advice', None) or '-'}<br>"
                row += f"&nbsp;&nbsp;- الإجراءات: {getattr(exam, 'planned_procedures', None) or '-'}<br>"
            else:
                row += "<i>⚠ لا يوجد فحص سريري لهذا الموعد</i><br>"

            rows.append(row)
        return format_html("<hr>".join(rows))
    appointment_history.short_description = "سجل المواعيد والفحوصات"


# ===========================
# Attachment
# ===========================
@admin.register(Attachment)
class AttachmentAdmin(admin.ModelAdmin):
    list_display = ["type", "medical_record", "uploaded_at"]
    search_fields = ["medical_record__patient__first_name", "medical_record__patient__last_name"]
    list_filter = ["type", "uploaded_at"]
    raw_id_fields = ["medical_record"]


# ===========================
# Medication
# ===========================
@admin.register(Medication)
class MedicationAdmin(admin.ModelAdmin):
    list_display = ["name", "default_dose_unit", "is_active"]
    search_fields = ["name"]
    list_filter = ["is_active"]


# ===========================
# PrescribedMedication
# ===========================
@admin.register(PrescribedMedication)
class PrescribedMedicationAdmin(admin.ModelAdmin):
    list_display = [
        "medication", "clinical_exam",
        "times_per_day", "dose_unit", "number_of_days",
        "prescribed_by", "prescribed_at",
    ]
    search_fields = [
        "medication__name",
        "clinical_exam__patient__first_name",
        "clinical_exam__patient__last_name",
    ]
    list_filter = ["prescribed_by", "prescribed_at"]
    raw_id_fields = ["clinical_exam", "medication", "prescribed_by"]


# ===========================
# MedicationPackage (+ items)
# ===========================
@admin.register(MedicationPackage)
class MedicationPackageAdmin(admin.ModelAdmin):
    list_display = ["name", "disease", "is_active", "created_at", "items_count"]
    search_fields = ["name", "disease__name"]
    list_filter = ["is_active", "disease"]
    inlines = [MedicationPackageItemInline]

    def items_count(self, obj):
        return obj.items.count()
    items_count.short_description = "عدد الأدوية"


# ===========================
# AppliedMedicationPackage
# ===========================
@admin.register(AppliedMedicationPackage)
class AppliedMedicationPackageAdmin(admin.ModelAdmin):
    list_display = ["package", "clinical_exam", "prescribed_by", "mode", "prescribed_at"]
    list_filter = ["mode", "prescribed_by", "prescribed_at", "package__disease"]
    search_fields = [
        "package__name",
        "package__disease__name",
        "clinical_exam__patient__first_name",
        "clinical_exam__patient__last_name",
    ]
    raw_id_fields = ["clinical_exam", "package", "prescribed_by"]
