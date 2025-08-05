from rest_framework import serializers
from .models import (
    MedicalRecord,
    ChronicDisease,
    Attachment,
    Medication,
    PrescribedMedication
)
from procedures.models import ClinicalExam
from accounts.models import Doctor
from patients.models import Patient
from appointment.models import Appointment


# -----------------------------
# Patient (Basic Info)
# -----------------------------
class PatientBasicSerializer(serializers.ModelSerializer):
    class Meta:
        model = Patient
        fields = [
            'id', 'first_name', 'last_name',
            'date_of_birth', 'gender',
            'phone', 'email', 'address'
        ]


# -----------------------------
# Doctor (Basic Info)
# -----------------------------
class DoctorBasicSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(source='user.get_full_name', read_only=True)
    
    class Meta:
        model = Doctor
        fields = ['id', 'full_name']


# -----------------------------
# Medication (Definition)
# -----------------------------
class MedicationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Medication
        fields = ['id', 'name', 'description', 'default_dose_unit', 'is_active']
        read_only_fields = ['id']


# -----------------------------
# Prescribed Medication (Nested inside clinical exam)
# -----------------------------
class PrescribedMedicationNestedSerializer(serializers.ModelSerializer):
    medication_name = serializers.CharField(source='medication.name', read_only=True)

    class Meta:
        model = PrescribedMedication
        fields = [
            'id', 'medication_name',
            'times_per_day', 'dose_unit',
            'number_of_days', 'notes',
            'prescribed_at'
        ]


# -----------------------------
# Clinical Exam (Nested inside appointment)
# -----------------------------
class ClinicalExamNestedSerializer(serializers.ModelSerializer):
    medications = PrescribedMedicationNestedSerializer(many=True, read_only=True)

    class Meta:
        model = ClinicalExam
        fields = [
            'id', 'complaint', 'medical_advice',
            'planned_procedures', 'created_at',
            'medications'
        ]


# -----------------------------
# Appointment with doctor and exam
# -----------------------------
class AppointmentNestedSerializer(serializers.ModelSerializer):
    doctor = DoctorBasicSerializer(read_only=True)
    clinicalexam = ClinicalExamNestedSerializer(read_only=True)

    class Meta:
        model = Appointment
        fields = [
            'id', 'date', 'time', 'status', 'reason',
            'doctor', 'clinicalexam'
        ]


# -----------------------------
# Chronic Disease
# -----------------------------
class ChronicDiseaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChronicDisease
        fields = ['id', 'medical_record', 'disease_name', 'notes', 'diagnosed_at']
        read_only_fields = ['id']


# -----------------------------
# Attachment
# -----------------------------
class AttachmentSerializer(serializers.ModelSerializer):
    type_display = serializers.CharField(source='get_type_display', read_only=True)

    class Meta:
        model = Attachment
        fields = [
            'id', 'medical_record', 'file', 'type',
            'type_display', 'description', 'uploaded_at'
        ]
        read_only_fields = ['id', 'uploaded_at', 'type_display']


# -----------------------------
# Medical Record (Basic)
# -----------------------------
class MedicalRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = MedicalRecord
        fields = ['id', 'patient', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


# -----------------------------
# Medical Record (Detailed View)
# -----------------------------
class MedicalRecordDetailSerializer(serializers.ModelSerializer):
    patient = PatientBasicSerializer(read_only=True)
    chronic_diseases = ChronicDiseaseSerializer(many=True, read_only=True)
    attachments = AttachmentSerializer(many=True, read_only=True)
    appointments = serializers.SerializerMethodField()

    class Meta:
        model = MedicalRecord
        fields = [
            'id', 'patient', 'created_at', 'updated_at',
            'chronic_diseases', 'attachments', 'appointments'
        ]

    def get_appointments(self, obj):
        patient = obj.patient
        appointments = Appointment.objects.filter(patient=patient).select_related('doctor').order_by('-date')
        return AppointmentNestedSerializer(appointments, many=True).data
