from rest_framework import serializers
from .models import Patient
import re

class PatientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Patient
        fields = [
            'id', 'first_name', 'last_name', 'date_of_birth', 'gender',
            'phone', 'email', 'address', 'doctor',
            'created_at', 'updated_at', 'is_archived',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def validate_first_name(self, value):
        if value.isdigit():
            raise serializers.ValidationError("First name cannot be only numbers.")
        return value

    def validate_last_name(self, value):
        if value.isdigit():
            raise serializers.ValidationError("Last name cannot be only numbers.")
        return value

    def validate_phone(self, value):
        if not re.match(r'^\+?\d{7,15}$', value):
            raise serializers.ValidationError("Phone number must contain only digits and may start with '+'.")
        if Patient.objects.filter(phone=value).exclude(id=self.instance.id if self.instance else None).exists():
            raise serializers.ValidationError("Phone number already exists.")
        return value

    def validate_email(self, value):
        if value and Patient.objects.filter(email=value).exclude(id=self.instance.id if self.instance else None).exists():
            raise serializers.ValidationError("Email already exists.")
        return value

    def create(self, validated_data):
        """إنشاء مريض جديد بعد التحقق"""
        return super().create(validated_data)

    def update(self, instance, validated_data):
        """تحديث بيانات مريض بعد التحقق"""
        return super().update(instance, validated_data)
