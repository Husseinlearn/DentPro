from django.shortcuts import render
from rest_framework import generics, status, views, permissions
from rest_framework.response import Response

from .models import (
    ClinicalExam,
    ClinicalExamItem,
    ProcedureCategory,
    DentalProcedure,
    Toothcode,
)
from .serializers import (
    ClinicalExamSerializer,
    ClinicalExamItemSerializer,
    ClinicalExamSubmitSerializer,
    ProcedureCategorySerializer,
    ProcedureCategoryDetailSerializer,
    DentalProcedureSerializer,
    ToothcodeSerializer,
)

# ---------------------------
# ClinicalExam
# ---------------------------
class ClinicalExamListCreateAPIView(generics.ListCreateAPIView):
    queryset = ClinicalExam.objects.select_related("patient", "doctor", "appointment").all()
    serializer_class = ClinicalExamSerializer
    filterset_fields = ["patient", "doctor", "appointment"]
    search_fields = ["complaint", "medical_advice"]  # لا يوجد planned_procedures الآن
    ordering_fields = ["created_at"]


class ClinicalExamRUDAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = ClinicalExam.objects.select_related("patient", "doctor", "appointment").all()
    serializer_class = ClinicalExamSerializer


# عند الضغط على "حفظ" من الواجهة: إنشاء/تحديث الفحص + إنشاء عناصر (إجراء × سن) دفعة واحدة
class ClinicalExamSubmitAPIView(generics.CreateAPIView):
    # permission_classes = [permissions.IsAuthenticated]   # عدّل حسب نظامك
    serializer_class = ClinicalExamSubmitSerializer


# ---------------------------
# Dictionary: Categories & Procedures
# ---------------------------
class ProcedureCategoryListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = ProcedureCategorySerializer

    def get_queryset(self):
        qs = ProcedureCategory.objects.all()
        if self.request.method == "GET":
            qs = qs.prefetch_related("procedures")
        return qs

    def get_serializer_class(self):
        if self.request.method == "GET":
            return ProcedureCategoryDetailSerializer
        return ProcedureCategorySerializer


class ProcedureCategoryRUDAPIView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ProcedureCategorySerializer

    def get_queryset(self):
        qs = ProcedureCategory.objects.all()
        if self.request.method == "GET":
            qs = qs.prefetch_related("procedures")
        return qs

    def get_serializer_class(self):
        if self.request.method == "GET":
            return ProcedureCategoryDetailSerializer
        return ProcedureCategorySerializer


class DentalProcedureListCreateAPIView(generics.ListCreateAPIView):
    queryset = DentalProcedure.objects.select_related("category").all()
    serializer_class = DentalProcedureSerializer
    filterset_fields = ["is_active", "category"]
    search_fields = ["name", "description"]


class DentalProcedureRUDAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = DentalProcedure.objects.select_related("category").all()
    serializer_class = DentalProcedureSerializer


# ---------------------------
# Toothcode
# ---------------------------
class ToothcodeListAPIView(generics.ListAPIView):
    queryset = Toothcode.objects.all()
    serializer_class = ToothcodeSerializer
    filterset_fields = ["tooth_type", "tooth_number"]
    search_fields = ["tooth_number", "description"]
    ordering_fields = ["tooth_type", "tooth_number"]


# ---------------------------
# ClinicalExam Items (إجراء × سن)
# ---------------------------
class ClinicalExamItemListCreateAPIView(generics.ListCreateAPIView):
    queryset = ClinicalExamItem.objects.select_related(
        "clinical_exam", "procedure", "toothcode", "performed_by"
    ).all()
    serializer_class = ClinicalExamItemSerializer
    filterset_fields = ["clinical_exam", "procedure", "toothcode", "performed_by"]
    ordering_fields = ["created_at"]


class ClinicalExamItemRUDAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = ClinicalExamItem.objects.select_related(
        "clinical_exam", "procedure", "toothcode", "performed_by"
    ).all()
    serializer_class = ClinicalExamItemSerializer
