from django.urls import path
from . import views
urlpatterns = [
    path('clinical-exams/', views.ClinicalExamListCreateView.as_view(), name='clinical-exam-list-create'),
    path('clinical-exams/<int:pk>/', views.ClinicalExamDetailView.as_view(), name='clinical-exam-detail'),
]
