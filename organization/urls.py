from django.urls import path
from .views import add_organisation, add_pic

app_name = 'organization'

urlpatterns = [
    path('add/', add_organisation, name="add_organization"),
    path('add/add_pic/', add_pic, name="add_pic"),
]
