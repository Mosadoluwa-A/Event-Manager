from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import UserChangeForm, UserCreationForm
from .models import Convener, Event
from django.utils.translation import gettext_lazy as _


class UserChangeForm(UserChangeForm):
    class Meta:
        field_classes = None


class UserCreationForm(UserCreationForm):
    class Meta:
        model = Convener
        fields = ("email",)
        field_classes = None


class ConvenerAdmin(UserAdmin):
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name')}),
        (_('Permissions'), {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'email_verified', 'groups', 'user_permissions'),
        }),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2'),
        }),
    )
    list_display = ("email", "first_name", "is_staff", "email_verified")
    search_fields = ('email', 'first_name', 'last_name')
    ordering = ('email',)
    form = UserChangeForm
    add_form = UserCreationForm


class EventAdmin(admin.ModelAdmin):
    list_display = ("name", "convener", "location", "total_mrun_slots", "total_cchal_slots")


admin.site.register(Convener, ConvenerAdmin)
admin.site.register(Event, EventAdmin)


