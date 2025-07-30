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
        errors = {}
        doctor = data.get('doctor', getattr(self.instance, 'doctor', None))
        patient = data.get('patient', getattr(self.instance, 'patient', None))
        date_ = data.get('date', getattr(self.instance, 'date', None))
        time_ = data.get('time', getattr(self.instance, 'time', None))

        # 1. التاريخ لا يمكن أن يكون في الماضي
        if date_ < date.today():
            errors['date'] = "لا يمكن اختيار تاريخ سابق لحجز الموعد."

        # 2. منع حجز موعد للطبيب في نفس الوقت (ما لم يكن ملغيًا)
        if Appointment.objects.filter(
            doctor=doctor,
            date=date_,
            time=time_
        ).exclude(status='ملغي').exclude(id=getattr(self.instance, 'id', None)).exists():
            errors['time'] = "الطبيب لديه موعد آخر في نفس التاريخ والوقت."

        # 3. منع حجز موعد للمريض في نفس الوقت (ما لم يكن ملغيًا)
        if Appointment.objects.filter(
            patient=patient,
            date=date_,
            time=time_
        ).exclude(status='ملغي').exclude(id=getattr(self.instance, 'id', None)).exists():
            errors['time'] = "المريض لديه موعد آخر في نفس التاريخ والوقت."

        # 4. المريض لا يمكنه حجز أكثر من موعد قادم (مؤكد أو معلق فقط)
        active_statuses = ['مؤكد', 'معلق']
        if Appointment.objects.filter(
            patient=patient,
            date__gte=date.today(),
            status__in=active_statuses
        ).exclude(id=getattr(self.instance, 'id', None)).exists():
            errors['patient'] = "المريض لديه موعد قادم بالفعل ولا يمكن حجز أكثر من موعد في نفس الفترة."

        if errors:
            raise serializers.ValidationError(errors)

        return data