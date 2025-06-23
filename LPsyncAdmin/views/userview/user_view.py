from django.shortcuts import render, redirect
from LPsyncAdmin.models.usermodel import User
import random
from django.core.mail import send_mail
from django.conf import settings

def signup(request):
    if request.method == "POST":
        try:
            user = User.objects.get(email=request.POST['email'])
            return render(request, "usertemplate/signup.html", {'error': 'Email already exists'})
        except User.DoesNotExist:
            if request.POST['pswd'] == request.POST['cpswd']:
                User.objects.create(
                    username = request.POST['username'],
                    email = request.POST['email'],
                    pswd = request.POST['pswd'],
                    cpswd = request.POST['cpswd']
                )
                return redirect('base')
            else:
                return render(request, "usertemplate/signup.html", {'error': 'Passwords do not match'})
    else:
        return render(request, "usertemplate/signup.html")

def login(request):
    if request.method == "POST":
        try:
            user=User.objects.get(email=request.POST['email'], pswd=request.POST['pswd'])
            request.session['email'] = user.email
            request.session['pswd'] = user.pswd
            return redirect('base')
        except User.DoesNotExist:
            return render(request, "usertemplate/login.html", {'error': 'Invalid email or password'})
    else:
        return render(request, "usertemplate/login.html")

def logout(request):
    if 'email' in request.session:
        del request.session['email']
    if 'pswd' in request.session:
        del request.session['pswd']
    return redirect('login')

def fpswd(request):
    if request.method == "POST":
        try:
            user = User.objects.get(email=request.POST['email'])
            subject = "Password Reset Request"
            otp = random.randint(100000, 999999)
            message = f"HI {user.username}, \n\nYour OTP for password reset is: -" + str(otp)
            email_from = settings.EMAIL_HOST_USER
            recipient_list = [user.email ,]
            send_mail(subject, message, email_from, recipient_list)
            return render(request, "usertemplate/v_otp.html", {'email': user.email, 'otp': str(otp)})
        except User.DoesNotExist:
            return render(request, "usertemplate/fpswd.html", {'error': 'Email not found'})
    else:
        return render(request, "usertemplate/fpswd.html")

def verify_otp(request):
    email = request.POST['email']
    uotp = request.POST['uotp']
    otp = request.POST['otp']
    if request.method == "POST":
        if uotp == otp:
            return render(request, "usertemplate/new_pswd.html", {'email': email})
        else:
            return render(request, "usertemplate/fpswd.html", {'error': 'Invalid OTP', 'email': email, 'otp': otp})
    else:
        return render(request, "usertemplate/v_otp.html", {'email': email, 'otp': otp})

def new_pswd(request):
    if request.method == 'POST': 
        email = request.POST['email']
        npswd = request.POST['npswd']
        cnpswd = request.POST['cnpswd']
        if npswd == cnpswd:
            user=User.objects.get(email=email)
            user.pswd = npswd
            user.cpswd = cnpswd
            user.save()
            return redirect('login')
        else:
            return render(request, "usertemplate/new_pswd.html", {'error': 'Passwords do not match', 'email': email})
    else:
        return render(request, "usertemplate/new_pswd.html")