# appointments/serializers.py

from rest_framework import serializers
from .models import Appointment
from datetime import date

class AppointmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Appointment
        fields = [
            'id', 'patient', 'doctor',
            'date', 'time', 'status', 'reason', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']
    def validate(self, data):
        if data['date'] < date.today():  #  المقارنة الصحيحة
            raise serializers.ValidationError("لا يمكن حجز موعد في تاريخ سابق.")
        return data