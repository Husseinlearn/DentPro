from rest_framework import serializers
from .models import (
    CustomUser, UserProfile,
    Role, UserRole,
    Doctor
)
from django.contrib.auth.password_validation import validate_password



class UserProfileNestedSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ['phone', 'gender', 'birth_date', 'address', 'image']


class DoctorNestedSerializer(serializers.ModelSerializer):
    class Meta:
        model = Doctor
        fields = ['specialization', 'license_number', 'revenue_share']


class UnifiedUserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True)
    profile = UserProfileNestedSerializer()
    doctor_profile = DoctorNestedSerializer(required=False)
    
    user_type = serializers.ChoiceField(choices=[
        ('admin', 'Admin'),
        ('receptionist', 'Receptionist'),
        ('assistant', 'Assistant'),
        ('manager', 'Manager'),
        ('doctor', 'Doctor')
    ])

    class Meta:
        model = CustomUser
        fields = [
                    'id',
                    'username', 
                    'email', 
                    'first_name',
                    'last_name',
                    'user_type', 
                    'password', 
                    'password2', 
                    'profile', 
                    'doctor_profile'
                    ]

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Passwords do not match"})

        if attrs.get('user_type') == 'doctor' and 'doctor_profile' not in self.initial_data:
            raise serializers.ValidationError({"doctor_profile": "Doctor data is required for user_type 'doctor'"})
        return attrs

    def create(self, validated_data):
        profile_data = validated_data.pop('profile')
        doctor_data = validated_data.pop('doctor_profile', None)
        password = validated_data.pop('password')
        validated_data.pop('password2')

        user = CustomUser.objects.create_user(**validated_data)
        user.set_password(password)
        user.save()

        UserProfile.objects.create(user=user, **profile_data)

        if validated_data['user_type'] == 'doctor' and doctor_data:
            Doctor.objects.create(user=user, **doctor_data)

        return user

    def update(self, instance, validated_data):
        profile_data = validated_data.pop('profile', {})
        doctor_data = validated_data.pop('doctor_profile', {})

        instance.username = validated_data.get('username', instance.username)
        instance.email = validated_data.get('email', instance.email)
        instance.user_type = validated_data.get('user_type', instance.user_type)

        if 'password' in validated_data and validated_data['password']:
            instance.set_password(validated_data['password'])

        instance.save()

        profile = instance.profile
        for attr, value in profile_data.items():
            setattr(profile, attr, value)
        profile.save()

        if instance.user_type == 'doctor' and hasattr(instance, 'doctor_profile'):
            doctor = instance.doctor_profile
            for attr, value in doctor_data.items():
                setattr(doctor, attr, value)
            doctor.save()

        return instance