from django.urls import path
from . import views


urlpatterns = [
    path('', views.AppointmentCreateAPIView.as_view(), name='appointment-list-create'),
    path('list/', views.AppointmentListAPIView.as_view(), name='list-appointments'),
    path('update/<int:id>/', views.AppointmentUpdateAPIView.as_view(), name='update-appointment'),
]