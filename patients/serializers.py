from rest_framework import serializers
from .models import Patient

import re
from datetime import date


class PatientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Patient
        fields = [
            'id',
            'first_name',
            'last_name',
            'date_of_birth',
            'gender',
            'phone',
            'email',
            'address',
            'created_at',
            'updated_at',
            'is_archived',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    #  التحقق من الاسم الأول
    def validate_first_name(self, value):
        if not value.strip().isalpha():
            raise serializers.ValidationError("First name must contain only letters.")
        return value

    #  التحقق من الاسم الأخير
    def validate_last_name(self, value):
        if not value.strip().isalpha():
            raise serializers.ValidationError("Last name must contain only letters.")
        return value

    #  التحقق من تاريخ الميلاد
    def validate_date_of_birth(self, value):
        if value > date.today():
            raise serializers.ValidationError("Date of birth cannot be in the future.")
        return value

    #  التحقق من الجنس
    def validate_gender(self, value):
        allowed = ['Male', 'Female', 'Other']
        if value not in allowed:
            raise serializers.ValidationError(f"Gender must be one of: {', '.join(allowed)}.")
        return value

    #  التحقق من رقم الهاتف
    def validate_phone(self, value):
        if not re.match(r'^\+?\d{7,15}$', value):
            raise serializers.ValidationError("Phone number must contain only digits and may start with '+'.")
        if Patient.objects.filter(phone=value).exclude(id=self.instance.id if self.instance else None).exists():
            raise serializers.ValidationError("Phone number already exists.")
        return value
    def validate_gender(self, value):
        allowed = ['male', 'female', 'other']
        normalized = value.strip().lower()
        if normalized not in allowed:
            raise serializers.ValidationError(f"Gender must be one of: {', '.join(allowed)}.")
        return normalized
    #  التحقق من البريد الإلكتروني
    def validate_email(self, value):
        if value and Patient.objects.filter(email=value).exclude(id=self.instance.id if self.instance else None).exists():
            raise serializers.ValidationError("Email already exists.")
        return value

    #  التحقق من العنوان
    def validate_address(self, value):
        if len(value.strip()) < 5:
            raise serializers.ValidationError("Address is too short.")
        return value

    #  دالة الإنشاء
    def create(self, validated_data):
        return Patient.objects.create(**validated_data)

    #  دالة التعديل
    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance