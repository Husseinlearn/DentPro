from django.shortcuts import render
from rest_framework import generics, views, status
from rest_framework.response import Response

from .models import (
    MedicalRecord,
    ChronicDisease,
    Attachment,
    Medication
)

from .serializers import (
    MedicalRecordSerializer,
    ChronicDiseaseSerializer,
    AttachmentSerializer,
    MedicationSerializer,
    MedicalRecordDetailSerializer
)

#  السجل الطبي
class MedicalRecordListCreateAPIView(generics.ListCreateAPIView):
    queryset = MedicalRecord.objects.all()
    serializer_class = MedicalRecordSerializer


class MedicalRecordRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = MedicalRecord.objects.all()
    serializer_class = MedicalRecordSerializer


#  عرض سجل طبي كامل حسب المريض
class MedicalRecordByPatientAPIView(views.APIView):
    def get(self, request, patient_id):
        try:
            record = MedicalRecord.objects.get(patient__id=patient_id)
        except MedicalRecord.DoesNotExist:
            return Response(
                {"detail": "Medical record not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = MedicalRecordDetailSerializer(record)
        return Response(serializer.data, status=status.HTTP_200_OK)


#  الأمراض المزمنة
class ChronicDiseaseListCreateAPIView(generics.ListCreateAPIView):
    queryset = ChronicDisease.objects.all()
    serializer_class = ChronicDiseaseSerializer


class ChronicDiseaseRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = ChronicDisease.objects.all()
    serializer_class = ChronicDiseaseSerializer


#  المرفقات
class AttachmentListCreateAPIView(generics.ListCreateAPIView):
    queryset = Attachment.objects.all()
    serializer_class = AttachmentSerializer


class AttachmentRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Attachment.objects.all()
    serializer_class = AttachmentSerializer


#  الأدوية
class MedicationListCreateAPIView(generics.ListCreateAPIView):
    queryset = Medication.objects.filter(is_active=True)
    serializer_class = MedicationSerializer


class MedicationRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Medication.objects.all()
    serializer_class = MedicationSerializer
