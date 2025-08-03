from django.contrib import admin
from . models import ClinicalExam
# Register your models here.


@admin.register(ClinicalExam)
class ClinicalExamAdmin(admin.ModelAdmin):
    list_display = ('id', 'patient', 'doctor', 'appointment', 'created_at')
    search_fields = ('patient__name', 'doctor__name', 'complaint')
    list_filter = ('doctor', 'created_at')
    ordering = ('-created_at',)
    readonly_fields = ('created_at',)
    
    def has_add_permission(self, request):
        return True