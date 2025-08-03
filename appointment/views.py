from django.shortcuts import render
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics, permissions
from .models import Appointment
from .serializers import AppointmentSerializer
from datetime import date
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