from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import login, logout, authenticate
from django.core.mail import send_mail
from .forms import ConvenerLogin
from convener.models import Convener
from organization.models import Organization, gen_code
import string
from datetime import datetime, timedelta


def home(request):
    orgs = Organization.objects.all()
    return render(request, 'home.html', {"orgs": orgs})

# Auth


def login_user(request):
    if request.method == "POST":
        user = authenticate(request, email=request.POST['email'], password=request.POST['password'])
        if user is None:
            return render(request, '404.html')
        token = gen_code(size=5, chars=string.digits)
        tok_gen_time = str(datetime.now())
        mail_subj = "Your one time password"
        mail_body = f"Your password is: {token}. This password is valid for 15 minutes "
        send_mail(mail_subj, mail_body, from_email=None, recipient_list=[user.email])
        request.session['user_email'] = user.email
        request.session['token'] = token
        request.session['tok_gen_time'] = tok_gen_time
        request.session['allow_mfa'] = True
        return redirect(validate_mfa)

    form = ConvenerLogin
    return render(request, 'login.html', {"form": form})


def validate_mfa(request):
    if request.method == "POST":
        try:
            token = request.POST['otp']
            tok_gen_time = request.session['tok_gen_time']
            token_expiry = datetime.fromisoformat(tok_gen_time) + timedelta(minutes=15)
            if token == request.session['token'] and datetime.now() < token_expiry:
                request.session['allow_mfa'] = False
                user_email = request.session['user_email']
                user = Convener.objects.get(email=user_email)
                login(request, user)
                messages.success(request, "Login Success")
                return redirect(home)
            messages.error(request, "OTP is invalid!")
            return render(request, 'mfa.html')
        except KeyError:
            messages.error(request, "OTP is invalid!")
            return render(request, 'mfa.html')
    elif request.method == "GET" and request.session['allow_mfa'] is True:
        try:
            return render(request, 'mfa.html')
        except KeyError:
            messages.error(request, "OTP is invalid!")
            return render(request, '404.html')
    else:
        return render(request, '404.html')


def resend_token(request):
    if request.method == "POST":
        resend_otp = bool(request.POST['resend_otp'])
        if resend_otp is True:
            new_otp = gen_code(size=5, chars=string.digits)
            new_tok_gen_time = str(datetime.now())
            print("Sending mail...")
            mail_subj = "Your one time password"
            mail_body = f"Your new password is: {new_otp}. This password is valid for 15 minutes "
            send_mail(mail_subj, mail_body, from_email=None, recipient_list=[request.session['user_email']])
            print("Mail Sent!")
            request.session['token'] = new_otp
            request.session['tok_gen_time'] = new_tok_gen_time
            return render(request, 'mfa.html')
    return render(request, '404.html')


def logout_user(request):
    if request.method == "POST":
        logout(request)
        return redirect(login_user)
