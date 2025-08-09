from rest_framework import serializers
from .models import Patient
from datetime import datetime
import re
from datetime import date

class FlexibleDateField(serializers.DateField):
    def to_internal_value(self, value):
        if isinstance(value, date):
            return value
        if isinstance(value, str):
            for fmt in ("%Y-%m-%d", "%d-%m-%Y", "%d/%m/%Y"):
                try:
                    return datetime.strptime(value, fmt).date()
                except ValueError:
                    continue
        raise serializers.ValidationError("تاريخ الميلاد بتنسيق خاطئ. استخدم YYYY-MM-DD أو DD-MM-YYYY أو DD/MM/YYYY.")
class PatientSerializer(serializers.ModelSerializer):
    date_of_birth = FlexibleDateField()
    class Meta:
        model = Patient
        fields = [
            'id',
            'first_name',
            'last_name',
            'date_of_birth',
            'gender',
            'phone',
            'email',
            'address',
            'created_at',
            'updated_at',
            'is_archived',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def validate(self, data):
        full_name = f"{data.get('first_name', '').strip()} {data.get('last_name', '').strip()}"
        parts = full_name.split()
        if len(parts) < 4:
            raise serializers.ValidationError("يجب أن يحتوي الاسم الكامل على أربع كلمات على الأقل (الاسم الأول والثاني والثالث والأخير مجتمعين).")
        return data

    # #  التحقق من الاسم الأول
    # def validate_first_name(self, value):
    #     if not value.strip().isalpha():
    #         raise serializers.ValidationError("First name must contain only letters.")
    #     return value

    # #  التحقق من الاسم الأخير
    # def validate_last_name(self, value):
    #     if not value.strip().isalpha():
    #         raise serializers.ValidationError("Last name must contain only letters.")
    #     return value

    # ✅ التحقق من تنسيق وتاريخ الميلاد
def validate_date_of_birth(self, value):
    from datetime import datetime, date

    # إذا كانت القيمة نصية (string) نحللها
    if isinstance(value, str):
        for fmt in ("%Y-%m-%d", "%d-%m-%Y", "%d/%m/%Y"):
            try:
                value = datetime.strptime(value, fmt).date()
                break
            except ValueError:
                continue
        else:
            raise serializers.ValidationError("تاريخ الميلاد بتنسيق خاطئ. استخدم YYYY-MM-DD أو DD-MM-YYYY.")

    # إذا كانت القيمة كائن datetime نحولها إلى date فقط
    elif isinstance(value, datetime):
        value = value.date()

    # تحقق أن التاريخ ليس في المستقبل
    if value > date.today():
        raise serializers.ValidationError("لا يمكن أن يكون تاريخ الميلاد في المستقبل.")

    return value

    #  التحقق من الجنس
    def validate_gender(self, value):
        val = value.strip().lower()
        accepted = ['male', 'female', 'other', 'ذكر', 'أنثى', 'انثى', 'غير ذلك', 'اخر', 'آخر']
        if val not in accepted:
            raise serializers.ValidationError(
                "Gender must be one of: ذكر، أنثى، غير ذلك أو male, female, other."
            )
        return value.strip()
    #  التحقق من رقم الهاتف
    def validate_phone(self, value):
        if not re.match(r'^7\d{8}$', value):
            raise serializers.ValidationError("رقم الهاتف يجب أن يبدأ بـ 7 ويتكون من 9 أرقام. مثل (7XXXXXXXX).")

        # تحقق من عدم التكرار
        if Patient.objects.filter(phone=value).exclude(id=self.instance.id if self.instance else None).exists():
            raise serializers.ValidationError("رقم التلفون موجود مسبقاً.")

        return value
    
    #  التحقق من البريد الإلكتروني
    def validate_email(self, value):
        if value and Patient.objects.filter(email=value).exclude(id=self.instance.id if self.instance else None).exists():
            raise serializers.ValidationError("الايميل موجود مسبقاً.")
        return value

    #  التحقق من العنوان
    def validate_address(self, value):
        if len(value.strip()) < 2:
            raise serializers.ValidationError("العنوان قصير جدا.")
        return value

    #  دالة الإنشاء
    def create(self, validated_data):
        return Patient.objects.create(**validated_data)

    #  دالة التعديل
    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance