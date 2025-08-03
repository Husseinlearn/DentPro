from django.shortcuts import render
from rest_framework import generics
from .models import ClinicalExam
from .serializers import ClinicalExamSerializer

# Create your views here.
class ClinicalExamListCreateView(generics.ListCreateAPIView):
    """
    عرض وإنشاء جلسات الفحص السريري
    """
    queryset = ClinicalExam.objects.all()
    serializer_class = ClinicalExamSerializer


class ClinicalExamDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    عرض أو تعديل أو حذف جلسة فحص سريري واحدة
    """
    queryset = ClinicalExam.objects.all()
    serializer_class = ClinicalExamSerializer
