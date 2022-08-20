from django.contrib import admin
from .models import Organization, PIC, Category, Participant, Policy
from convener.admin import ConvenerAdmin
from django.utils.translation import gettext_lazy as _


class OrganizationAdmin(admin.ModelAdmin):
    list_display = ("name", "person_in_charge", "mrun_code", "cchal_code", "mrun_slots", "cchal_slots")
    exclude = ("mrun_code", "cchal_code")


class PICAdmin(ConvenerAdmin):
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name', 'phone_no')}),
        (_('Permissions'), {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'email_verified', 'groups', 'user_permissions'),
        }),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )
    list_display = ("email", "first_name", "phone_no", "is_staff", "email_verified")


class ParticipantAdmin(admin.ModelAdmin):
    list_display = ("reg_id", "first_name", "last_name", "email", "gender", "organization", "category")
    exclude = ["reg_id"]


admin.site.register(Organization, OrganizationAdmin)
admin.site.register(PIC, PICAdmin)
admin.site.register(Category)
admin.site.register(Participant, ParticipantAdmin)
admin.site.register(Policy)
