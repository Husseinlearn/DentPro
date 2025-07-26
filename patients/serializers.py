from rest_framework import serializers
from .models import Patient
from accounts.models import Doctor
from django.contrib.auth import get_user_model
import re

class PatientSerializer(serializers.ModelSerializer):
    doctor_name = serializers.CharField(write_only=True, required=False)  # اسم الطبيب كإدخال
    doctor_display = serializers.CharField(source='doctor.full_name', read_only=True)  # لعرض اسم الطبيب بدل ID

    class Meta:
        model = Patient
        fields = [
            'id', 'first_name', 'last_name', 'date_of_birth', 'gender',
            'phone', 'email', 'address',
            'doctor', 'doctor_name', 'doctor_display',
            'created_at', 'updated_at', 'is_archived',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'doctor']

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
        User = get_user_model()
        doctor_name = validated_data.pop('doctor_name', None)
        if doctor_name:
            try:
                # نحاول فصل الاسم إلى اسم أول واسم أخير
                first_name, last_name = doctor_name.strip().split(" ", 1)
                # البحث عن المستخدم
                user = User.objects.get(first_name__iexact=first_name, last_name__iexact=last_name)
                # البحث عن الطبيب المرتبط بهذا المستخدم
                doctor = Doctor.objects.get(user=user)
                validated_data['doctor'] = doctor
            except ValueError:
                raise serializers.ValidationError({'doctor_name': "Doctor name must include first and last name separated by a space."})
            except User.DoesNotExist:
                raise serializers.ValidationError({'doctor_name': f"No user found with name '{doctor_name}'."})
            except Doctor.DoesNotExist:
                raise serializers.ValidationError({'doctor_name': f"No doctor found for user '{doctor_name}'."})

        return super().create(validated_data)

    def update(self, instance, validated_data):
        doctor_name = validated_data.pop('doctor_name', None)
        if doctor_name:
            try:
                doctor = Doctor.objects.get(full_name__iexact=doctor_name)
                validated_data['doctor'] = doctor
            except Doctor.DoesNotExist:
                raise serializers.ValidationError({'doctor_name': f"Doctor '{doctor_name}' not found."})
        return super().update(instance, validated_data)
