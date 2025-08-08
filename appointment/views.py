from django.shortcuts import render
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics, permissions
from .models import Appointment
from .serializers import AppointmentSerializer, AppointmentStatusUpdateSerializer
from datetime import date
from rest_framework import status
from rest_framework.response import Response
# Create your views here.
class AppointmentCreateAPIView(generics.CreateAPIView):
    queryset = Appointment.objects.all()
    serializer_class = AppointmentSerializer
    # permission_classes = [permissions.IsAuthenticated]


class AppointmentListAPIView(generics.ListAPIView):
    queryset = Appointment.objects.all().order_by('-date', '-time')
    serializer_class = AppointmentSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['doctor', 'patient', 'date', 'status']
    # permission_classes = [permissions.IsAuthenticated]

class AppointmentUpdateAPIView(generics.RetrieveUpdateAPIView):
    queryset = Appointment.objects.all()
    serializer_class = AppointmentSerializer
    # permission_classes = [permissions.IsAuthenticated]  
    lookup_field = 'id'  

class AppointmentDetailAPIView(generics.RetrieveAPIView):
    queryset = Appointment.objects.select_related('patient', 'doctor__user').all()
    serializer_class = AppointmentSerializer
    lookup_field = 'id'  # تأكد أن id هو UUID أو Int حسب الموديل

class TodayAppointmentsAPIView(generics.ListAPIView):
    serializer_class = AppointmentSerializer

    def get_queryset(self):
        today = date.today()
        return Appointment.objects.filter(date=today).order_by('time')
class AppointmentStatusUpdateAPIView(generics.UpdateAPIView):
    queryset = Appointment.objects.all()
    serializer_class = AppointmentStatusUpdateSerializer
    lookup_field = 'id'  # تأكد أنك تستخدم UUID أو Int حسب الموديل

    def patch(self, request, *args, **kwargs):
        appointment = self.get_object()
        serializer = self.get_serializer(appointment, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({
            "message": "تم تحديث حالة الموعد بنجاح.",
            "appointment_id": str(appointment.id),
            "new_status": serializer.data['status']
        }, status=status.HTTP_200_OK)