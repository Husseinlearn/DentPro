from django.db import models
import uuid
from django.utils.translation import gettext_lazy as _
# Create your models here.

# --------------------------------------------------------------------
# Patient Model: جدول  المرضى 
class Patient(models.Model):
    GENDER_CHOICES = [
        ('male', _('Male')),
        ('female', _('Female')),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    first_name = models.CharField(max_length=100, verbose_name=_("First Name"))
    last_name = models.CharField(max_length=100, verbose_name=_("Last Name"))
    date_of_birth = models.DateField(verbose_name=_("Date of Birth"), null=True, blank=True)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, verbose_name=_("Gender"), null=True, blank=True)
    phone = models.CharField(max_length=20, verbose_name=_("Phone"), unique=True)
    email = models.EmailField(verbose_name=_("Email"), null=True, blank=True, unique=True)
    address = models.TextField(verbose_name=_("Address"), null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Created At"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Updated At"))
    is_archived = models.BooleanField(default=False, verbose_name=_("Archived"))

    def __str__(self):
        return f"{self.first_name} {self.last_name}"