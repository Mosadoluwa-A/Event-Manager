from django.forms import ModelForm, CharField
from .models import Organization, Participant, Team


class OrganizationAddForm(ModelForm):
    # person_in_charge = CharField()

    class Meta:
        model = Organization
        fields = ['name', 'person_in_charge', 'mrun_slots', 'cchal_slots']


class ParticipantAddForm(ModelForm):
    class Meta:
        model = Participant
        fields = ['first_name', 'last_name', 'email', 'gender', 'country']


class CreateTeamForm(ModelForm):
    class Meta:
        model = Team
        fields = ['name', 'motto']