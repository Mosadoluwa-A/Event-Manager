from django.contrib import admin
from .models import Convener, Event


class ConvenerAdmin(admin.ModelAdmin):
    list_display = ("email", "first_name", "is_staff")


class EventAdmin(admin.ModelAdmin):
    list_display = ("name", "convener", "location", "total_mrun_slots", "total_cchal_slots")


admin.site.register(Convener, ConvenerAdmin)
admin.site.register(Event, EventAdmin)


