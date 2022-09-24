from django.shortcuts import render, redirect, reverse
from django.contrib.auth import get_user
from django.contrib import messages
from django.db.models import Q
from django.core.mail import send_mail
from django.core.cache import cache
from .models import PIC, Organization, Category, Policy, Participant, Team
from convener.models import Event
from .forms import OrganizationAddForm, ParticipantAddForm, CreateTeamForm
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
                    cache.set('reg_id', org_reg_id, 900)
                    # request.session['org_id'] = org.id
                    cache.set('org_id', org.id, 900)
                    cache.set('category', "Mass Run", 900)
                    return redirect("organization:add_participant")
            except Exception as e:
                print(e)
                messages.error(request, "Organization does not exist")
                return redirect(check_org)
        elif is_chief_challenge(org_reg_id):
            try:
                org = Organization.objects.get(cchal_code=org_reg_id)
                if org.cchal_slots != 0:
                    cache.set('reg_id', org_reg_id, 900)
                    cache.set('org_id', org.id, 900)
                    cache.set('category', "Mass Run", 900)
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
        cache.set('first_name', first_name)
        cache.set('last_name', last_name)
        cache.set('gender', gender)
        cache.set('email', email)
        cache.set('email2', email2)
        cache.set('country', country)
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
            cache.set('reg_id', part_reg_id, 900)
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
            cache.set('participant_id', new_participant.id, 900)
            cache.set('par_reg_id', new_participant.reg_id, 900)
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
                cache.set("auth", True, 900)
                cache.set("email", email, 900)
                cache.set("par_reg_id", participant.reg_id, 900)
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
    except Exception as e:
        print(e)
        messages.error(request, 'You need to be verified')
        return redirect("organization:par_status")


def par_logout(request):
    if request.method == "POST":
        cache.delete('auth')
        return redirect('organization:par_status')


def create_team(request):
    if request.method == "POST":
        if request.user.is_anonymous:
            reg_id = cache.get('par_reg_id')
            participant = Participant.objects.get(reg_id=reg_id)
            creator = participant.email
            category = participant.category
            form = CreateTeamForm(request.POST)
            if form.is_valid() and participant.team is None:
                new_team = form.save(commit=False)
                new_team.category = category
                new_team.creator = creator
                new_team.save()
                cache.set("team_id", new_team.id, 900)
                participant.team = new_team
                participant.save()
                print(f"The team of the participant {participant.team}")
                return redirect('organization:team_home')
            messages.error(request, "You can only be in one team at a time")
            return redirect('organization:add_team')
        else:
            creator = request.user.email
            organisation = request.user.organizations.first()
            form = CreateTeamForm(request.POST)
            if form.is_valid():
                new_team = form.save(commit=False)
                new_team.creator = creator
                new_team.save()
                cache.set("team_id", new_team.id, 900)
                organisation.team = new_team
                organisation.save()
                return redirect('organization:team_home')
            messages.error(request, "Please fill all fields")
            return redirect(create_team)
    return render(request, 'add_team.html')


def team_home(request):
    if request.method == "GET":
        team_id = cache.get("team_id")
        print(f"The team id is {team_id}")
        team = Team.objects.get(id=team_id)
        return render(request, 'team_home.html', {"team": team})
    return render(request, '404.html')


def join_team(request):
    if request.method == "POST":
        team = request.POST['team']
        try:
            team_obj = Team.objects.get(name__iexact=team)
            reg_id = cache.get("par_reg_id")
            participant = Participant.objects.get(reg_id=reg_id)
            if team_obj and team_obj.participants.all().count() < 4:
                if team_obj.category == participant.category and participant.team is None:
                    participant.team = team_obj
                    participant.save()
                    cache.set("team_id", team_obj.id)
                    return redirect("organization:team_home")
                messages.error(request, "You cannot join a team outside your category")
                return redirect("organization:join_team")
            messages.error(request, "The team does not exist or has run out slots try another")
            return redirect("organization:join_team")
        except Exception as e:
            print(e)
            messages.error(request, "You cannot join a team outside your category")
            return redirect("organization:join_team")
    return render(request, 'join_team.html')