from django.shortcuts import render
from rest_framework import generics, status, views
from rest_framework.response import Response

from .models import (
    ClinicalExam, ProcedureCategory, DentalProcedure,
    Toothcode, Procedure, ProcedureToothcode
)
from .serializers import (
    ClinicalExamSerializer, ProcedureCategorySerializer, DentalProcedureSerializer,
    ToothcodeSerializer, ProcedureSerializer, ProcedureToothcodeSerializer,
    ProcedureAttachTeethSerializer, ProcedureCategoryDetailSerializer
)

# ---------------------------
# ClinicalExam
# ---------------------------
class ClinicalExamListCreateAPIView(generics.ListCreateAPIView):
    queryset = ClinicalExam.objects.select_related("patient", "doctor", "appointment").all()
    serializer_class = ClinicalExamSerializer
    filterset_fields = ["patient", "doctor", "appointment"]
    search_fields = ["complaint", "medical_advice", "planned_procedures"]
    ordering_fields = ["created_at"]

class ClinicalExamRUDAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = ClinicalExam.objects.select_related("patient", "doctor", "appointment").all()
    serializer_class = ClinicalExamSerializer


# ---------------------------
# Dictionary: Categories & Procedures
# ---------------------------

# فئات الإجراءات: قائمة/إنشاء — نُظهر الإجراءات التابعة عند GET فقط
class ProcedureCategoryListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = ProcedureCategorySerializer  # الافتراضي (للإنشاء)

    def get_queryset(self):
        qs = ProcedureCategory.objects.all()
        # عند القراءة فقط، نُحمّل الإجراءات المرتبطة لتفادي N+1
        if self.request.method == "GET":
            qs = qs.prefetch_related("procedures")
        return qs

    def get_serializer_class(self):
        # عند GET نعرض الفئة مع الإجراءات
        if self.request.method == "GET":
            return ProcedureCategoryDetailSerializer
        return ProcedureCategorySerializer


# فئة واحدة: عرض/تعديل/حذف — مع الإجراءات عند GET
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
# Execution: Procedure & links
# ---------------------------
class ProcedureListCreateAPIView(generics.ListCreateAPIView):
    queryset = Procedure.objects.select_related("definition", "category", "clinical_exam").all()
    serializer_class = ProcedureSerializer
    filterset_fields = ["clinical_exam", "definition", "category", "status"]
    search_fields = ["name", "description"]
    ordering_fields = ["created_at", "cost", "status"]

class ProcedureRUDAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Procedure.objects.select_related("definition", "category", "clinical_exam").all()
    serializer_class = ProcedureSerializer


class ProcedureToothcodeListCreateAPIView(generics.ListCreateAPIView):
    queryset = ProcedureToothcode.objects.select_related("procedure", "toothcode", "performed_by").all()
    serializer_class = ProcedureToothcodeSerializer
    filterset_fields = ["procedure", "toothcode", "performed_by"]
    ordering_fields = ["performed_at", "created_at"]

class ProcedureToothcodeRUDAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = ProcedureToothcode.objects.all()
    serializer_class = ProcedureToothcodeSerializer


# ---------------------------
# Bulk attach teeth
# ---------------------------
class ProcedureAttachTeethAPIView(views.APIView):
    def post(self, request):
        ser = ProcedureAttachTeethSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        created = ser.save()
        return Response({"created": len(created)}, status=status.HTTP_201_CREATED)
