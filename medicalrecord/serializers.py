# medicalrecord/serializers.py
from rest_framework import serializers

from .models import (
    MedicalRecord,
    Attachment,
    Medication,
    PrescribedMedication,
    MedicationPackage,
    MedicationPackageItem,
    AppliedMedicationPackage,
)

from procedures.models import ClinicalExam
from accounts.models import Doctor
from patients.models import Patient, PatientAllergy, PatientDisease
from appointment.models import Appointment


# -------------------------------------------------
# Patient (Basic)
# -------------------------------------------------
class PatientBasicSerializer(serializers.ModelSerializer):
    class Meta:
        model = Patient
        fields = [
            "id", "first_name", "last_name",
            "date_of_birth", "gender",
            "phone", "email", "address"
        ]


# -------------------------------------------------
# Doctor (Basic)
# -------------------------------------------------
class DoctorBasicSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(source="user.get_full_name", read_only=True)

    class Meta:
        model = Doctor
        fields = ["id", "full_name"]


# -------------------------------------------------
# Medication (Definition)
# -------------------------------------------------
class MedicationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Medication
        fields = ["id", "name", "description", "default_dose_unit", "is_active"]
        read_only_fields = ["id"]


# -------------------------------------------------
# Prescribed Medication (read / nested)
# -------------------------------------------------
class PrescribedMedicationNestedSerializer(serializers.ModelSerializer):
    medication_name = serializers.CharField(source="medication.name", read_only=True)

    class Meta:
        model = PrescribedMedication
        fields = [
            "id", "medication_name",
            "times_per_day", "dose_unit",
            "number_of_days", "notes",
            "prescribed_at",
        ]


# (full serializer for create/update via API)
class PrescribedMedicationSerializer(serializers.ModelSerializer):
    medication_name = serializers.CharField(source="medication.name", read_only=True)

    class Meta:
        model = PrescribedMedication
        fields = [
            "id", "clinical_exam", "medication", "medication_name",
            "times_per_day", "dose_unit", "number_of_days",
            "notes", "prescribed_by", "prescribed_at",
        ]
        read_only_fields = ["id", "prescribed_at"]

    # تعبئة الموصي تلقائياً من المستخدم إن وُجد
    def create(self, validated_data):
        request = self.context.get("request")
        doctor = getattr(getattr(request, "user", None), "doctor", None)
        if doctor and "prescribed_by" not in validated_data:
            validated_data["prescribed_by"] = doctor
        return super().create(validated_data)


# -------------------------------------------------
# Clinical Exam (Nested inside appointment)
# ملاحظة: تم حذف planned_procedures حسب اتفاقنا
# -------------------------------------------------
class ClinicalExamNestedSerializer(serializers.ModelSerializer):
    # الملاحظة العامة للوصفة (تمت إضافتها في Model: ClinicalExam)
    prescription_notes = serializers.CharField(read_only=True)

    # قائمة الأدوية الموصوفة داخل الفحص
    medications = PrescribedMedicationNestedSerializer(
        many=True, read_only=True, source="prescribed_medications"
    )

    class Meta:
        model = ClinicalExam
        fields = [
            "id",
            "complaint",
            "medical_advice",
            "prescription_notes",  # ملاحظات الوصفة العامة
            "created_at",
            "medications",
        ]


# -------------------------------------------------
# Appointment with doctor and exam
# -------------------------------------------------
class AppointmentNestedSerializer(serializers.ModelSerializer):
    doctor = DoctorBasicSerializer(read_only=True)
    clinical_exam = ClinicalExamNestedSerializer(read_only=True)

    class Meta:
        model = Appointment
        fields = [
            "id", "date", "time", "status", "reason",
            "doctor", "clinical_exam",
        ]


# -------------------------------------------------
# Attachment
# -------------------------------------------------
class AttachmentSerializer(serializers.ModelSerializer):
    type_display = serializers.CharField(source="get_type_display", read_only=True)

    class Meta:
        model = Attachment
        fields = [
            "id", "medical_record", "file", "type",
            "type_display", "description", "uploaded_at",
        ]
        read_only_fields = ["id", "uploaded_at", "type_display"]


# -------------------------------------------------
# Patient Diseases & Allergies (read-only mirrors)
# -------------------------------------------------
class PatientDiseaseReadSerializer(serializers.ModelSerializer):
    disease_name = serializers.CharField(source="disease.name", read_only=True)

    class Meta:
        model = PatientDisease
        fields = ["id", "disease", "disease_name", "notes", "diagnosed_at"]


class PatientAllergyReadSerializer(serializers.ModelSerializer):
    medication_name = serializers.CharField(source="medication.name", read_only=True)

    class Meta:
        model = PatientAllergy
        fields = ["id", "medication", "medication_name"]


# -------------------------------------------------
# Medical Record (Basic)
# -------------------------------------------------
class MedicalRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = MedicalRecord
        fields = ["id", "patient", "created_at", "updated_at"]
        read_only_fields = ["id", "created_at", "updated_at"]


# -------------------------------------------------
# Medical Record (Detailed)
# -------------------------------------------------
class MedicalRecordDetailSerializer(serializers.ModelSerializer):
    patient = PatientBasicSerializer(read_only=True)
    attachments = AttachmentSerializer(many=True, read_only=True)
    appointments = serializers.SerializerMethodField()

    diseases = PatientDiseaseReadSerializer(
        source="patient.patient_diseases", many=True, read_only=True
    )
    allergies = PatientAllergyReadSerializer(
        source="patient.patient_allergies", many=True, read_only=True
    )

    class Meta:
        model = MedicalRecord
        fields = [
            "id", "patient", "created_at", "updated_at",
            "diseases", "allergies",
            "attachments", "appointments",
        ]

    def get_appointments(self, obj):
        qs = (
            Appointment.objects
            .filter(patient=obj.patient)
            .select_related("doctor")
            .order_by("-date")
        )
        return AppointmentNestedSerializer(qs, many=True).data


# =================================================
#              Medication Packages (CRUD)
# =================================================
class MedicationPackageItemSerializer(serializers.ModelSerializer):
    medication_name = serializers.CharField(source="medication.name", read_only=True)

    class Meta:
        model = MedicationPackageItem
        fields = [
            "id", "medication", "medication_name",
            "times_per_day", "dose_unit", "number_of_days", "notes",
        ]
        read_only_fields = ["id", "medication_name"]


class MedicationPackageSerializer(serializers.ModelSerializer):
    disease_name = serializers.CharField(source="disease.name", read_only=True)
    items = MedicationPackageItemSerializer(many=True)

    class Meta:
        model = MedicationPackage
        fields = [
            "id", "name", "disease", "disease_name",
            "description", "is_active", "items", "created_at",
        ]
        read_only_fields = ["id", "disease_name", "created_at"]

    def create(self, validated_data):
        items_data = validated_data.pop("items", [])
        pkg = MedicationPackage.objects.create(**validated_data)
        for item in items_data:
            MedicationPackageItem.objects.create(package=pkg, **item)
        return pkg

    def update(self, instance, validated_data):
        items_data = validated_data.pop("items", None)
        for attr, val in validated_data.items():
            setattr(instance, attr, val)
        instance.save()
        if items_data is not None:
            instance.items.all().delete()
            for item in items_data:
                MedicationPackageItem.objects.create(package=instance, **item)
        return instance


# -------------------------------------------------
# Apply Medication Package to a Clinical Exam (action)
# -------------------------------------------------
class ApplyMedicationPackageSerializer(serializers.Serializer):
    clinical_exam_id = serializers.IntegerField()
    mode = serializers.ChoiceField(choices=("append", "replace"), default="append")

    def validate(self, attrs):
        pkg: MedicationPackage = self.context["package"]
        if not pkg.is_active:
            raise serializers.ValidationError("هذه الحزمة غير مفعلة.")
        try:
            exam = ClinicalExam.objects.get(pk=attrs["clinical_exam_id"])
        except ClinicalExam.DoesNotExist:
            raise serializers.ValidationError("الفحص السريري غير موجود.")
        attrs["exam"] = exam
        attrs["doctor"] = getattr(getattr(self.context.get("request"), "user", None), "doctor", None)
        return attrs

    def create(self, validated_data):
        pkg: MedicationPackage = self.context["package"]
        exam = validated_data["exam"]
        doctor = validated_data.get("doctor")
        mode = validated_data["mode"]

        if mode == "replace":
            PrescribedMedication.objects.filter(clinical_exam=exam).delete()

        created_ids = []
        for item in pkg.items.all():
            pm = PrescribedMedication.objects.create(
                clinical_exam=exam,
                medication=item.medication,
                times_per_day=item.times_per_day,
                dose_unit=item.dose_unit,
                number_of_days=item.number_of_days,
                notes=item.notes,
                prescribed_by=doctor,
            )
            created_ids.append(pm.id)

        AppliedMedicationPackage.objects.create(
            clinical_exam=exam, package=pkg, prescribed_by=doctor, mode=mode
        )
        return {"created_ids": created_ids, "count": len(created_ids), "mode": mode, "package_id": pkg.id}


# =================================================
# Create a full prescription (General notes + items)
# =================================================
class PrescriptionItemInputSerializer(serializers.Serializer):
    medication = serializers.PrimaryKeyRelatedField(queryset=Medication.objects.filter(is_active=True))
    times_per_day = serializers.IntegerField(min_value=1)
    dose_unit = serializers.CharField(max_length=50)
    number_of_days = serializers.IntegerField(min_value=1)
    notes = serializers.CharField(allow_blank=True, required=False)

class PrescriptionUpsertSerializer(serializers.Serializer):
    clinical_exam = serializers.PrimaryKeyRelatedField(queryset=ClinicalExam.objects.all())
    general_notes = serializers.CharField(allow_blank=True, required=False)
    items = PrescriptionItemInputSerializer(many=True)

    def validate(self, attrs):
        if not attrs.get("items"):
            raise serializers.ValidationError("يجب إضافة دواء واحد على الأقل.")
        return attrs

    def create(self, validated_data):
        exam = validated_data["clinical_exam"]
        # حفظ الملاحظة العامة
        exam.prescription_notes = validated_data.get("general_notes") or None
        exam.save(update_fields=["prescription_notes"])

        request = self.context.get("request")
        prescribed_by = getattr(getattr(request, "user", None), "doctor", None)

        created = []
        for it in validated_data["items"]:
            pm = PrescribedMedication.objects.create(
                clinical_exam=exam,
                medication=it["medication"],
                times_per_day=it["times_per_day"],
                dose_unit=it["dose_unit"],
                number_of_days=it["number_of_days"],
                notes=it.get("notes") or None,
                prescribed_by=prescribed_by,
            )
            created.append(pm)

        # رجّع تمثيل غني يحتوي نفس المدخلات + أسماء الأدوية وتواريخ الإنشاء
        items_repr = []
        for pm in created:
            items_repr.append({
                "id": pm.id,
                "medication": pm.medication.id,
                "medication_name": pm.medication.name,
                "times_per_day": pm.times_per_day,
                "dose_unit": pm.dose_unit,
                "number_of_days": pm.number_of_days,
                "notes": pm.notes,
                "prescribed_by": getattr(pm.prescribed_by, "id", None),
                "prescribed_at": pm.prescribed_at,
            })

        return {
            "clinical_exam": exam.id,
            "general_notes": exam.prescription_notes,
            "count": len(created),
            "items": items_repr,
        }
