from django.urls import path
from django.views.decorators.cache import cache_page
from . import views

app_name = 'organization'

urlpatterns = [
    path('add/', views.add_organisation, name="add_organization"),
    path('add/add_pic/', views.add_pic, name="add_pic"),
    path('participant/', views.check_org, name='participant'),
    path('participant/add', views.get_participant_data, name="add_participant"),
    path('participants/tna', cache_page(600)(views.terms_n_agrmnt), name="tna"),
    path('participant/confirm', views.add_participant, name="confirm_participant"),
    path('participant/reg-summary', views.reg_summary, name="reg_summary"),
    path('participant/status', views.participant_status, name='par_status'),
    path('participant/<int:par_id>', views.participant_home, name="par_home"),
    path('participant/resend_email', views.resend_email, name='resend_email'),
    path('participant/logout', views.par_logout, name='par_logout')
]
