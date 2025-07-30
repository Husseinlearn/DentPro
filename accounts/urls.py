from django.urls import path
from . import views


urlpatterns = [
    path('register_user/', views.register_user, name='register_user'),
    path('update_user/', views.update_user, name='update_user'),
    path('login_user/', views.login_user, name='login_user'),
    path('current_user/', views.current_user, name='current_user'),
    path('list_users/', views.list_users, name='list_users'),
    path('doctor_list/', views.DoctorListSimpleAPIView.as_view(), name='doctor_list'),
    # path('logout_user/', views.logout_user, name='logout_user'),
]