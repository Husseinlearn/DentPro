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

    def validate(self, data):
        full_name = f"{data.get('first_name', '').strip()} {data.get('last_name', '').strip()}"
        parts = full_name.split()
        if len(parts) < 4:
            raise serializers.ValidationError("Full name must contain at least four words (first and last name combined).")
        return data

    # #  التحقق من الاسم الأول
    # def validate_first_name(self, value):
    #     if not value.strip().isalpha():
    #         raise serializers.ValidationError("First name must contain only letters.")
    #     return value

    # #  التحقق من الاسم الأخير
    # def validate_last_name(self, value):
    #     if not value.strip().isalpha():
    #         raise serializers.ValidationError("Last name must contain only letters.")
    #     return value

    #  التحقق من تاريخ الميلاد
    def validate_date_of_birth(self, value):
        if value > date.today():
            raise serializers.ValidationError("Date of birth cannot be in the future.")
        return value

    #  التحقق من الجنس
    def validate_gender(self, value):
        val = value.strip().lower()
        accepted = ['male', 'female', 'other', 'ذكر', 'أنثى', 'انثى', 'غير ذلك', 'اخر', 'آخر']
        if val not in accepted:
            raise serializers.ValidationError(
                "Gender must be one of: ذكر، أنثى، غير ذلك أو male, female, other."
            )
        return value.strip()
    #  التحقق من رقم الهاتف
    def validate_phone(self, value):
        if not re.match(r'^0?7\d{8}$', value):
            raise serializers.ValidationError("Phone number must be a valid Yemeni number (e.g. +9677XXXXXXXX or 07XXXXXXXX).")

        # تحقق من عدم التكرار
        if Patient.objects.filter(phone=value).exclude(id=self.instance.id if self.instance else None).exists():
            raise serializers.ValidationError("Phone number already exists.")

        return value
    
    #  التحقق من البريد الإلكتروني
    def validate_email(self, value):
        if value and Patient.objects.filter(email=value).exclude(id=self.instance.id if self.instance else None).exists():
            raise serializers.ValidationError("Email already exists.")
        return value

    #  التحقق من العنوان
    def validate_address(self, value):
        if len(value.strip()) < 2:
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