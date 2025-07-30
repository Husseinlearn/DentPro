from django.shortcuts import render
from django_filters.rest_framework import DjangoFilterBackend
# Create your views here.

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
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['doctor', 'patient', 'date', 'status']
    # permission_classes = [permissions.IsAuthenticated]

class AppointmentUpdateAPIView(generics.RetrieveUpdateAPIView):
    queryset = Appointment.objects.all()
    serializer_class = AppointmentSerializer
    # permission_classes = [permissions.IsAuthenticated]  
    lookup_field = 'id'  
