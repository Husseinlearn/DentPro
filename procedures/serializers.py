from rest_framework import serializers
from .models import (
    ClinicalExam, ProcedureCategory, DentalProcedure,
    Toothcode, Procedure, ProcedureToothcode
)
from accounts.models import Doctor
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned

class FlexiblePKOrSlugRelatedField(serializers.Field):
    """
    حقل مرن لعلاقات الـ FK:
    - يقبل: رقم id (int أو str أرقام)، أو الاسم (slug_field) كسلسلة.
    - يقبل أيضًا dict مثل: {"id": 3} أو {"name": "..." }.
    - قابل لإعادة الاستخدام مع أي موديل عبر تمرير queryset و slug_field.
    - يمكن جعل الأولوية للاسم إذا كانت القيمة رقمية عبر prefer_slug=True.
    """
    def __init__(self, queryset, slug_field='name', prefer_slug=False, **kwargs):
        super().__init__(**kwargs)
        self.queryset = queryset
        self.slug_field = slug_field
        self.prefer_slug = prefer_slug  # مفيد لحقول قد تكون قيمتها رقمية مثل tooth_number

    def to_representation(self, value):
        # في الاستجابة أعِد الـ id (أبسط شيء)، ويمكن تخصيصه لو أردت
        return value.pk if value is not None else None

    def _get_by_pk(self, pk):
        return self.queryset.get(pk=pk)

    def _get_by_slug(self, slug):
        lookup = {f"{self.slug_field}__iexact": str(slug).strip()}
        return self.queryset.get(**lookup)

    def to_internal_value(self, data):
        # دعم dict: {"id": ..} أو {"<slug_field>": ".."}
        if isinstance(data, dict):
            if 'id' in data and data['id'] not in (None, ''):
                try:
                    return self._get_by_pk(int(data['id']))
                except (ValueError, ObjectDoesNotExist):
                    raise serializers.ValidationError(f"Object with id={data['id']} not found.")
            if self.slug_field in data and data[self.slug_field]:
                try:
                    return self._get_by_slug(data[self.slug_field])
                except MultipleObjectsReturned:
                    raise serializers.ValidationError(f"Multiple objects found for {self.slug_field}='{data[self.slug_field]}'. Please use id.")
                except ObjectDoesNotExist:
                    raise serializers.ValidationError(f"Object with {self.slug_field}='{data[self.slug_field]}' not found.")
            raise serializers.ValidationError(f"Provide either 'id' or '{self.slug_field}'.")

        # دعم رقم أو سلسلة
        if isinstance(data, int) or (isinstance(data, str) and data.strip() != ''):
            s = str(data).strip()
            is_digit = s.isdigit()

            # لو prefer_slug=True و القيمة رقمية، جرّب الاسم أولًا ثم id
            if is_digit and self.prefer_slug:
                try:
                    return self._get_by_slug(s)
                except MultipleObjectsReturned:
                    raise serializers.ValidationError(f"Multiple objects found for {self.slug_field}='{s}'. Please use id.")
                except ObjectDoesNotExist:
                    # لم نجد بالاسم، جرّب id
                    try:
                        return self._get_by_pk(int(s))
                    except ObjectDoesNotExist:
                        raise serializers.ValidationError(f"Object with id={s} not found.")
            # السيناريو العادي: جرّب id ثم الاسم
            if is_digit:
                try:
                    return self._get_by_pk(int(s))
                except ObjectDoesNotExist:
                    # لو لم يوجد كـ id، حاول كاسم
                    try:
                        return self._get_by_slug(s)
                    except MultipleObjectsReturned:
                        raise serializers.ValidationError(f"Multiple objects found for {self.slug_field}='{s}'. Please use id.")
                    except ObjectDoesNotExist:
                        raise serializers.ValidationError(f"Object not found by id or {self.slug_field}='{s}'.")
            # قيمة نصية غير رقمية => تعامل معها كاسم
            try:
                return self._get_by_slug(s)
            except MultipleObjectsReturned:
                raise serializers.ValidationError(f"Multiple objects found for {self.slug_field}='{s}'. Please use id.")
            except ObjectDoesNotExist:
                raise serializers.ValidationError(f"Object with {self.slug_field}='{s}' not found.")

        raise serializers.ValidationError("Invalid value type.")

# ===== Basic serializers =====
class ProcedureCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ProcedureCategory
        fields = ["id", "name", "description", "created_at"]
        read_only_fields = ["id", "created_at"]
    def validate_name(self, value):
        if ProcedureCategory.objects.filter(name__iexact=value.strip()).exists():
            raise serializers.ValidationError("هذا التصنيف موجود بالفعل.")
        return value.strip()


class DentalProcedureSerializer(serializers.ModelSerializer):
    category = FlexiblePKOrSlugRelatedField(
        queryset=ProcedureCategory.objects.all(),
        slug_field='name',        # نبحث بالاسم
        prefer_slug=False         # للأسماء عادةً مش رقمية
    )
    category_name = serializers.CharField(source="category.name", read_only=True)

    class Meta:
        model = DentalProcedure
        fields = ["id", "name", "description", "default_price", "is_active", "category", "category_name"]
        read_only_fields = ["id"]


class ToothcodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Toothcode
        fields = ["id", "tooth_number", "tooth_type", "description", "created_at"]
        read_only_fields = ["id", "created_at"]


class ClinicalExamSerializer(serializers.ModelSerializer):
    patient_display = serializers.SerializerMethodField()
    doctor_display = serializers.SerializerMethodField()

    class Meta:
        model = ClinicalExam
        fields = [
            "id", "patient", "doctor", "appointment",
            "complaint", "medical_advice", "planned_procedures",
            "created_at", "patient_display", "doctor_display",
        ]
        read_only_fields = ["id", "created_at", "patient_display", "doctor_display"]

    def get_patient_display(self, obj):
        return f"{obj.patient.first_name} {obj.patient.last_name}" if obj.patient_id else None

    def get_doctor_display(self, obj):
        return f"{obj.doctor.user.first_name} {obj.doctor.user.last_name}" if obj.doctor_id else None


# ===== Execution serializers =====
class ProcedureToothcodeSerializer(serializers.ModelSerializer):
    tooth_number = serializers.CharField(source="toothcode.tooth_number", read_only=True)
    tooth_type = serializers.CharField(source="toothcode.tooth_type", read_only=True)

    class Meta:
        model = ProcedureToothcode
        fields = [
            "id", "procedure", "toothcode", "tooth_number", "tooth_type",
            "performed_by", "notes", "performed_at", "created_at",
        ]
        read_only_fields = ["id", "performed_at", "created_at", "tooth_number", "tooth_type"]


class ProcedureSerializer(serializers.ModelSerializer):
    # يقبل id أو name لكلا الحقلين
    definition = FlexiblePKOrSlugRelatedField(
        queryset=DentalProcedure.objects.all(),
        slug_field='name',
        prefer_slug=False
    )
    category = FlexiblePKOrSlugRelatedField(
        queryset=ProcedureCategory.objects.all(),
        slug_field='name',
        prefer_slug=False,
        required=False, allow_null=True
    )

    teeth = ProcedureToothcodeSerializer(source="tooth_links", many=True, read_only=True)
    definition_name = serializers.CharField(source="definition.name", read_only=True)
    category_name = serializers.CharField(source="category.name", read_only=True)

    class Meta:
        model = Procedure
        fields = [
            "id", "clinical_exam", "definition", "definition_name", "category", "category_name",
            "name", "description", "cost", "status", "created_at", "teeth",
        ]
        read_only_fields = ["id", "created_at", "definition_name", "category_name", "teeth"]

    def validate(self, data):
        return data

    def create(self, validated_data):
        definition = validated_data.get("definition")
        if definition:
            validated_data.setdefault("name", definition.name)
            validated_data.setdefault("description", definition.description)
            if validated_data.get("cost") in (None, ""):
                validated_data["cost"] = definition.default_price
            if not validated_data.get("category") and getattr(definition, "category_id", None):
                validated_data["category_id"] = definition.category_id
        return super().create(validated_data)

    def update(self, instance, validated_data):
        definition = validated_data.get("definition")
        if definition:
            validated_data.setdefault("name", definition.name)
            if validated_data.get("description") in (None, ""):
                validated_data["description"] = definition.description
            if validated_data.get("cost") in (None, ""):
                validated_data["cost"] = definition.default_price
            if not validated_data.get("category") and getattr(definition, "category_id", None):
                validated_data["category_id"] = definition.category_id
        return super().update(instance, validated_data)

    def update(self, instance, validated_data):
        # عند ربط تعريف جديد، عَبّي القيم المفقودة فقط
        definition = validated_data.get("definition")
        if definition:
            validated_data.setdefault("name", definition.name)
            if validated_data.get("description") in (None, ""):
                validated_data["description"] = definition.description
            if validated_data.get("cost") in (None, ""):
                validated_data["cost"] = definition.default_price
            if not validated_data.get("category") and definition.category_id:
                validated_data["category_id"] = definition.category_id
        return super().update(instance, validated_data)


# ===== Bulk attach teeth =====
class ProcedureAttachTeethItemSerializer(serializers.Serializer):
    toothcode = FlexiblePKOrSlugRelatedField(
        queryset=Toothcode.objects.all(),
        slug_field='tooth_number',
        prefer_slug=True  # لأن tooth_number ممكن يكون رقم أيضًا، نعطي الأولوية له
    )
    performed_by = serializers.PrimaryKeyRelatedField(queryset=Doctor.objects.all(), required=False, allow_null=True)
    notes = serializers.CharField(required=False, allow_blank=True)


class ProcedureAttachTeethSerializer(serializers.Serializer):
    procedure = serializers.PrimaryKeyRelatedField(queryset=Procedure.objects.all())
    items = ProcedureAttachTeethItemSerializer(many=True)

    def create(self, validated_data):
        proc = validated_data["procedure"]
        items = validated_data["items"]
        objs = []
        for it in items:
            objs.append(ProcedureToothcode(
                procedure=proc,
                toothcode=it["toothcode"],
                performed_by=it.get("performed_by"),
                notes=it.get("notes", "")
            ))
        return ProcedureToothcode.objects.bulk_create(objs)

# class ClinicalExamSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = ClinicalExam
#         fields = [
#             'id',
#             'patient',
#             'doctor',
#             'appointment',
#             'complaint',
#             'medical_advice',
#             'planned_procedures',
#             'created_at',
#         ]
#         read_only_fields = ['id', 'created_at']