from django.shortcuts import render, redirect
from django.contrib.auth import get_user
from django.contrib import messages
from django.db.models import Q
from .models import PIC
from convener.models import Event
from .forms import OrganizationAddForm
from convener.views import home

# Create your views here.


def add_organisation(request):
    if request.method == "POST":
        # pic = PIC.objects.get_or_create_user(request.POST['person_in_charge'])
        convener = get_user(request)
        event = Event.objects.get(Q(convener=convener, status='ongoing'))  # the overall event
        form = OrganizationAddForm(request.POST)
        if form.is_valid():
            new_org = form.save(commit=False)
            new_org.save()
            new_org.events.add(event)  # Add this organization to the event
            new_org.update_event(event)
            messages.success(request, "Organization Added Successfully")
            return redirect(home)
        print(form.errors)
    org_form = OrganizationAddForm
    pics = PIC.objects.all()
    return render(request, 'add-organization.html', {'form': org_form, 'pics': pics})


def add_pic(request):  # view to add pic with ajax
    if request.method == "POST":
        pic_email = request.POST['pic_email']
        print("The pic email got here")
        PIC.objects.create_user(email=pic_email)
        return render(request, 'add-organization.html')
