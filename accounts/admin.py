# from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import CustomUser, UserProfile, Doctor, Role, UserRole
from django.contrib.auth.admin import UserAdmin


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ('email', 'username', 'user_type', 'is_staff', 'is_superuser', 'is_archived')
    search_fields = ('email', 'username')
    list_filter = ('user_type', 'is_staff', 'is_superuser', 'is_archived')
    ordering = ('email',)
    fieldsets = UserAdmin.fieldsets + (
        (None, {'fields': ('user_type', 'is_archived')}),
    )


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone', 'gender', 'birth_date')
    search_fields = ('user__email', 'phone')


@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):
    list_display = ('user', 'specialization', 'license_number')
    search_fields = ('user__email', 'specialization', 'license_number')


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ('name',)


@admin.register(UserRole)
class UserRoleAdmin(admin.ModelAdmin):
    list_display = ('user', 'role')
    list_filter = ('role__name',)
