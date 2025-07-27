from django.shortcuts import render

# Create your views here.
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, generics, filters
from .models import Patient
from .serializers import PatientSerializer
from django.shortcuts import get_object_or_404
from .filters import PatientFilter
from django_filters.rest_framework import DjangoFilterBackend


class PatientListCreateAPIView(generics.ListCreateAPIView):
    """عرض وإنشاء المرضى"""
    queryset = Patient.objects.filter(is_archived=False)
    serializer_class = PatientSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = PatientFilter
    #  البحث في هذه الحقول
    search_fields = ['first_name', 'last_name', 'phone', 'email', 'address']

    #  السماح بالترتيب حسب هذه الحقول
    ordering_fields = ['first_name', 'last_name', 'date_of_birth', 'created_at']
    ordering = ['created_at']  # ترتيب افتراضي
    # def get(self, request):
    #     patients = Patient.objects.filter(is_archived=False)
    #     serializer = PatientSerializer(patients, many=True)
    #     return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = PatientSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PatientRetrieveUpdateDestroyAPIView(APIView):
    """عرض وتعديل وحذف (أرشفة) مريض"""

    def get_object(self, pk):
        return get_object_or_404(Patient, pk=pk, is_archived=False)

    def get(self, request, pk):
        patient = self.get_object(pk)
        serializer = PatientSerializer(patient)
        return Response(serializer.data)

    def put(self, request, pk):
        patient = self.get_object(pk)
        serializer = PatientSerializer(patient, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        patient = self.get_object(pk)
        patient.delete()  # This will set is_archived to True
        return Response({'message': 'Patient Deleted successfully'},status=status.HTTP_204_NO_CONTENT)
