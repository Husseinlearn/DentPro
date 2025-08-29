"""
URL configuration for DentPro project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.http import HttpResponse 
from rest_framework_simplejwt.views import TokenObtainPairView
def health(_): return HttpResponse("ok")
urlpatterns = [
    path('health', health),
    path('admin/', admin.site.urls),
    path('api/accounts/', include('accounts.urls')),  # Include URLs from the accounts app
    path('api/patients/', include('patients.urls')),  # Include URLs from the patients app
    path('api/appointment/', include('appointment.urls')),  # Include URLs from the appointment app
    path('api/procedures/', include('procedures.urls')),  # Include URLs from the procedures app
    path('api/medical-record/', include('medicalrecord.urls')),  # Include URLs from the medicalrecord app
    path('api/billing/', include('billing.urls')),  # Include URLs from the billing app
    path('api/core/',include('core.urls')),  # Include URLs from the core app
    path('api-auth/', include('rest_framework.urls')),  # Include DRF authentication URLs
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),  # JWT token endpoint
]
