from django.forms import ModelForm, CharField
from .models import Organization


class OrganizationAddForm(ModelForm):
    # person_in_charge = CharField()

    class Meta:
        model = Organization
        fields = ['name', 'person_in_charge', 'mrun_slots', 'cchal_slots']
