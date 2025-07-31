from rest_framework import serializers
from datetime import date
from django.db.models import Q
from .models import Appointment
from accounts.models import Doctor
from patients.models import Patient
from django.db.models.functions import Concat
from django.db.models import Value as V
class AppointmentSerializer(serializers.ModelSerializer):
    # الحقول البديلة للإدخال بالاسم
    patient_name = serializers.CharField(write_only=True, required=False)
    doctor_name = serializers.CharField(write_only=True, required=False)

    # الحقول الأصلية (غير مطلوبة لأننا نملأها من الأسماء)
    patient = serializers.PrimaryKeyRelatedField(queryset=Patient.objects.all(), required=False)
    doctor = serializers.PrimaryKeyRelatedField(queryset=Doctor.objects.all(), required=False)

    # لعرض الأسماء في النتائج
    patient_display = serializers.SerializerMethodField()
    doctor_display = serializers.SerializerMethodField()

    class Meta:
        model = Appointment
        fields = [
            'id', 'patient', 'patient_name', 'patient_display',
            'doctor', 'doctor_name', 'doctor_display',
            'date', 'time', 'status', 'reason', 'created_at'
        ]
        read_only_fields = ['id', 'created_at', 'patient_display', 'doctor_display']

    #  عرض اسم المريض الكامل
    def get_patient_display(self, obj):
        return f"{obj.patient.first_name} {obj.patient.last_name}"

    #  عرض اسم الطبيب المرتبط بالمستخدم
    def get_doctor_display(self, obj):
        return obj.doctor.user.get_full_name()

    #  استبدال الأسماء بـ الكائنات قبل التحقق
    def to_internal_value(self, data):
        data = super().to_internal_value(data)

        patient_name = self.initial_data.get('patient_name')
        if patient_name and not data.get('patient'):
            try:
                first, last = patient_name.strip().split(" ", 1)
                patient = Patient.objects.get(
                    first_name__iexact=first.strip(),
                    last_name__iexact=last.strip()
                )
                data['patient'] = patient
            except Patient.DoesNotExist:
                raise serializers.ValidationError({"patient_name": "اسم المريض غير موجود."})

        # doctor_name = self.initial_data.get('doctor_name')
        doctor_name = data.pop('doctor_name', None)
        if not data.get('doctor') and doctor_name:
            try:
                doctor = Doctor.objects.annotate(
                    full_name=Concat('user__first_name', V(' '), 'user__last_name')
                ).get(full_name__iexact=doctor_name.strip())
                data['doctor'] = doctor
            except Doctor.DoesNotExist:
                raise serializers.ValidationError({"doctor_name": "اسم الطبيب غير موجود."})

        return data

    #  تحقق كامل للسيناريوهات السابقة
    def validate(self, data):
        errors = {}
        doctor = data.get('doctor', getattr(self.instance, 'doctor', None))
        patient = data.get('patient', getattr(self.instance, 'patient', None))
        date_ = data.get('date', getattr(self.instance, 'date', None))
        time_ = data.get('time', getattr(self.instance, 'time', None))

        # 1. التحقق من التاريخ
        if date_ and date_ < date.today():
            errors['date'] = "لا يمكن اختيار تاريخ سابق لحجز الموعد."

        # 2. منع الطبيب من وجود موعد بنفس الوقت
        if doctor and date_ and time_:
            if Appointment.objects.filter(
                doctor=doctor,
                date=date_,
                time=time_
            ).exclude(status='ملغي').exclude(id=getattr(self.instance, 'id', None)).exists():
                errors['time'] = "الطبيب لديه موعد آخر في نفس التاريخ والوقت."

        # 3. منع المريض من حجز في نفس الوقت
        if patient and date_ and time_:
            if Appointment.objects.filter(
                patient=patient,
                date=date_,
                time=time_
            ).exclude(status='ملغي').exclude(id=getattr(self.instance, 'id', None)).exists():
                errors['time'] = "المريض لديه موعد آخر في نفس التاريخ والوقت."

        # 4. منع المريض من حجز موعد قادم (غير ملغي أو منجز)
        active_statuses = ['مؤكد', 'معلق']
        if patient and date_ and time_:
            if Appointment.objects.filter(
                Q(date__gt=date_) | Q(date=date_, time__gt=time_),
                patient=patient,
                status__in=active_statuses
            ).exclude(id=getattr(self.instance, 'id', None)).exists():
                errors['patient'] = "المريض لديه موعد قادم بالفعل ولا يمكن حجز أكثر من موعد في نفس الفترة."

        if errors:
            raise serializers.ValidationError(errors)

        return data

    #  إزالة الحقول غير المرتبطة بالنموذج قبل إنشاء السجل
    def create(self, validated_data):
        validated_data.pop('patient_name', None)
        validated_data.pop('doctor_name', None)
        return super().create(validated_data)
