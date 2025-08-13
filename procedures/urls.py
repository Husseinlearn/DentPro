from django.urls import path
from . import views
from .views import *
urlpatterns = [
    # ClinicalExam
    path("clinical-exams/", ClinicalExamListCreateAPIView.as_view(), name="exam-list-create"),
    path("clinical-exams/<int:pk>/", ClinicalExamRUDAPIView.as_view(), name="exam-rud"),

    # Dictionary
    path("categories/", ProcedureCategoryListCreateAPIView.as_view(), name="category-list-create"),
    path("categories/<int:pk>/", ProcedureCategoryRUDAPIView.as_view(), name="category-rud"),
    path("dental-procedure/", DentalProcedureListCreateAPIView.as_view(), name="definition-list-create"),
    path("dental-procedure/<int:pk>/", DentalProcedureRUDAPIView.as_view(), name="definition-rud"),
    path("teeth/", ToothcodeListAPIView.as_view(), name="tooth-list"),

    # Execution
    path("procedures/", ProcedureListCreateAPIView.as_view(), name="procedure-list-create"),
    path("procedures/<int:pk>/", ProcedureRUDAPIView.as_view(), name="procedure-rud"),
    path("procedure-teeth/", ProcedureToothcodeListCreateAPIView.as_view(), name="procedure-tooth-list-create"),
    path("procedure-teeth/<int:pk>/", ProcedureToothcodeRUDAPIView.as_view(), name="procedure-tooth-rud"),

    # bulk attach teeth to a procedure
    path("procedures/attach-teeth/", ProcedureAttachTeethAPIView.as_view(), name="procedure-attach-teeth"),
]