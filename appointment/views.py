from django.shortcuts import render

# Create your views here.
# appointments/views.py

from rest_framework import generics, permissions
from .models import Appointment
from .serializers import AppointmentSerializer

class AppointmentCreateAPIView(generics.CreateAPIView):
    queryset = Appointment.objects.all()
    serializer_class = AppointmentSerializer
    # permission_classes = [permissions.IsAuthenticated]


class AppointmentListAPIView(generics.ListAPIView):
    queryset = Appointment.objects.all().order_by('-date', '-time')
    serializer_class = AppointmentSerializer
    permission_classes = [permissions.IsAuthenticated]
