from django.urls import path
from . import views


urlpatterns = [
    path('', views.AppointmentCreateAPIView.as_view(), name='appointment-list-create'),
    path('list/', views.AppointmentListAPIView.as_view(), name='list-appointments'),
    path('detailsapp/<int:id>/', views.AppointmentDetailAPIView.as_view(), name='appointment-detail'),
    path('update/<int:id>/', views.AppointmentUpdateAPIView.as_view(), name='update-appointment'),
    path('today/', views.TodayAppointmentsAPIView.as_view(), name='today-appointments'),
]