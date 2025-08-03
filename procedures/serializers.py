from rest_framework import serializers
from .models import ClinicalExam


class ClinicalExamSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClinicalExam
        fields = [
            'id',
            'patient',
            'doctor',
            'appointment',
            'complaint',
            'medical_advice',
            'planned_procedures',  # ✅ الحقل النصي الذي قررنا استخدامه
            'created_at',
        ]
        read_only_fields = ['id', 'created_at']
