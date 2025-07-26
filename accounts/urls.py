from django.urls import path
from . import views


urlpatterns = [
    path('api/register_user/', views.register_user, name='register_user'),
    path('api/update_user/', views.update_user, name='update_user'),
]