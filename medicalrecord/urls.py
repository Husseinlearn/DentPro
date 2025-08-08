from django.urls import path
from . import views

urlpatterns = [
    #  السجل الطبي
    path('medical-records/', views.MedicalRecordListCreateAPIView.as_view(), name='medicalrecord-list-create'),
    path('medical-records/<int:pk>/', views.MedicalRecordRetrieveUpdateDestroyAPIView.as_view(), name='medicalrecord-detail'),

    #  عرض السجل الطبي الكامل حسب المريض
    path('patients/<uuid:patient_id>/medical-record/', views.MedicalRecordByPatientAPIView.as_view(), name='medical-record-by-patient'),

    #  الأمراض المزمنة
    path('chronic-diseases/', views.ChronicDiseaseListCreateAPIView.as_view(), name='chronicdisease-list-create'),
    path('chronic-diseases/<int:pk>/', views.ChronicDiseaseRetrieveUpdateDestroyAPIView.as_view(), name='chronicdisease-detail'),

    #  المرفقات
    path('attachments/', views.AttachmentListCreateAPIView.as_view(), name='attachment-list-create'),
    path('attachments/<int:pk>/', views.AttachmentRetrieveUpdateDestroyAPIView.as_view(), name='attachment-detail'),

    #  الأدوية
    path('medications/', views.MedicationListCreateAPIView.as_view(), name='medication-list-create'),
    path('medications/<int:pk>/', views.MedicationRetrieveUpdateDestroyAPIView.as_view(), name='medication-detail'),
]
