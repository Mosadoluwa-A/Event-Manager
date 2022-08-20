from django.shortcuts import render, redirect, reverse
from django.contrib.auth import get_user
from django.contrib import messages
from django.db.models import Q
from django.core.mail import send_mail
from django.core.cache import cache
from .models import PIC, Organization, Category, Policy, Participant
from convener.models import Event
from .forms import OrganizationAddForm, ParticipantAddForm
from convener.views import home
from django_countries import countries

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
        PIC.objects.create_user(email=pic_email)
        return render(request, 'add-organization.html')


def is_mass_run(reg_id):
    if reg_id[:2] == "MR":
        return True
    return False


def is_chief_challenge(reg_id):
    if reg_id[:2] == "CC":
        return True
    return False


def get_category(reg_id):
    if is_mass_run(reg_id):
        category = Category.objects.get(name="Mass Run")
    elif is_chief_challenge(reg_id):
        category = Category.objects.get(name="Chief Challenge")
    return category


def update_slots(reg_id, org):
    if is_mass_run(reg_id):
        org.reduce_mrun_slots()
        msg = "Updated mass run slots"
    elif is_chief_challenge(reg_id):
        org.reduce_cchal_slots()
        msg = "Updated Chief Challenge Slots"
    return msg


def check_org(request):
    if request.method == "POST":
        org_reg_id = request.POST['reg_id']
        print(is_mass_run(org_reg_id))
        print(is_chief_challenge(org_reg_id))
        if is_mass_run(org_reg_id):
            try:

                org = Organization.objects.get(mrun_code=org_reg_id)

                if org.mrun_slots != 0:
                    cache.set('reg_id', org_reg_id, 600)
                    # request.session['org_id'] = org.id
                    cache.set('org_id', org.id, 600)
                    cache.set('category', "Mass Run", 600)
                    return redirect("organization:add_participant")
            except Exception as e:
                print(e)
                messages.error(request, "Organization does not exist")
                return redirect(check_org)
        elif is_chief_challenge(org_reg_id):
            try:
                org = Organization.objects.get(cchal_code=org_reg_id)
                if org.cchal_slots != 0:
                    cache.set('reg_id', org_reg_id, 600)
                    cache.set('org_id', org.id, 600)
                    cache.set('category', "Mass Run", 600)
                    return redirect("organization:add_participant")
            except Exception as e:
                print(e)
                messages.error(request, "Organization does not exist")
                return redirect("organization:participant")
    return render(request, 'participant_landing.html')


def get_participant_data(request):  # First view to get the data before passing to terms and agreement
    if request.method == "POST":
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        gender = request.POST['gender']
        email = request.POST['email']
        email2 = request.POST['email2']
        country = request.POST['country']
        cache.set('first_name', first_name, 600)
        cache.set('last_name', last_name, 600)
        cache.set('gender', gender, 600)
        cache.set('email', email, 600)
        cache.set('email2', email2, 600)
        cache.set('country', country, 600)
        return redirect("organization:tna")

    context = {"countries": countries}
    return render(request, 'add-participants.html', context)


def terms_n_agrmnt(request):
    if request.method == "POST":
        return redirect("organization:confirm_participant")
    privacy_statement = Policy.objects.get(name="Privacy Statement")
    return render(request, 'privacy_statement.html', {"privacy_statement": privacy_statement})


def add_participant(request):
    if request.method == "POST":
        reg_id = cache.get('reg_id')
        org_id = cache.get('org_id')
        org = Organization.objects.get(id=org_id)
        category = get_category(reg_id)
        email = request.POST['email']
        email2 = request.POST['email2']
        form = ParticipantAddForm(request.POST)
        if form.is_valid() and email == email2:
            new_participant = form.save(commit=False)
            new_participant.organization = org
            new_participant.category = category
            print(f"The new participant email is {new_participant.email}")
            new_participant.save()
            part_reg_id = new_participant.reg_id
            cache.set('reg_id', part_reg_id, 600)
            update_slots(reg_id, org)
            subj = "Bullcharge Confirmation Email"
            msg = f"This is to confirm your successful registration for bullcharge your registration code is {new_participant.reg_id}"
            recp = [new_participant.email]
            send_mail(
                subj,
                msg,
                from_email=None,
                recipient_list=recp,
                fail_silently=False,
            )
            cache.set('participant_id', new_participant.id, 600)
            cache.set('par_reg_id', new_participant.reg_id, 600)
            return redirect("organization:reg_summary")
        else:
            print(form.errors)
            messages.error(request, "Your emails don't match!")
            return redirect("organization:confirm_participant")
    else:
        first_name = cache.get('first_name')
        last_name = cache.get('last_name')
        gender = cache.get('gender')
        email = cache.get('email')
        email2 = cache.get('email2')
        context = {"first_name": first_name,
                   "last_name": last_name,
                   "gender": gender,
                   "email": email,
                   "email2": email2,
                   "countries": countries
                   }
        return render(request, 'preview-participants.html', context)


def reg_summary(request):
    first_name = cache.get('first_name')
    last_name = cache.get('last_name')
    gender = cache.get('gender')
    email = cache.get('email')
    country = cache.get('country')
    reg_id = cache.get('reg_id')
    category = cache.get('category')

    context = {
        "first_name": first_name,
        "last_name": last_name,
        "gender": gender,
        "email": email,
        "country": country,
        "reg_id": reg_id,
        "category": category
    }
    return render(request, 'registration-summary.html', context)


def participant_status(request):
    if request.method == "POST":
        reg_id = request.POST['reg_id']
        email = request.POST['email']
        try:
            participant = Participant.objects.get(Q(reg_id=reg_id), Q(email=email))
            if participant:
                cache.set("auth", True, 300)
                cache.set("email", email, 600)
                par_id = participant.id
                return redirect("organization:par_home", par_id)
        except Exception as e:
            print(f"The Exception is: {e}")
            messages.error(request, "You need to register")
            return redirect("organization:participant")
    return render(request, 'participant-status.html')


def resend_email(request):
    if request.method == "POST":
        resend_mail = bool(request.POST['resend_email'])
        if resend_mail is True:
            recep_email = cache.get('email')
            par_reg_id = cache.get('par_reg_id')
            subj = "Bullcharge Confirmation Email"
            msg = f"This is to confirm your successful registration for bullcharge your registration id is:{par_reg_id}"
            recp = [recep_email]
            send_mail(
                subj,
                msg,
                from_email=None,
                recipient_list=recp,
                fail_silently=False,
            )
            print("Email has been sent!")
            return render(request, 'participant.html')
    return render(request, '404.html')


def participant_home(request, par_id):
    try:
        auth = cache.get('auth')
        if auth:
            participant = Participant.objects.get(id=par_id)
            context = {"participant": participant}
            return render(request, 'participant.html', context)
        messages.error(request, 'You need to be verified')
        return redirect("organization:par_status")
    except:
        messages.error(request, 'You need to be verified')
        return redirect("organization:par_status")


def par_logout(request):
    if request.method == "POST":
        cache.delete('auth')
        return redirect('organization:par_status')
