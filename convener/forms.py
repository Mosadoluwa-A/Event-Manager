from django import forms
from django.forms import ModelForm
from .models import Convener


class ConvenerLogin(ModelForm):

    class Meta:
        model = Convener
        fields = ["email", "password"]

        widgets = {
            'password': forms.PasswordInput()
        }

