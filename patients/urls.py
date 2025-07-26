from django.urls import path
from . import views


urlpatterns = [
    path('api/patient/', views.PatientListCreateAPIView.as_view(), name='patient-list-create'),
    path('api/patient/<uuid:pk>/', views.PatientRetrieveUpdateDestroyAPIView.as_view(), name='patient-retrieve-update-destroy'),
]