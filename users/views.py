from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import get_user_model, login
from django.core.mail import send_mail
from django.urls import reverse
from django.contrib.auth.views import LoginView
from .forms import RegistrationForm
from django.contrib.auth.decorators import login_required

User = get_user_model()

class CustomLoginView(LoginView):
    template_name = "registration/login.html"

def index(request):
    return render(request, "index.html")

def register_user(request):
    if request.method == "POST":
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = True  
            user.is_verified = False 
            user.save()


            code = user.generate_verification_code()

            
            mail_subject = "Seu código de ativação - RebootVerde"
            message = f"Olá {user.username},\n\nSeu código de verificação é: {code}\nUse este código para ativar sua conta no site."
            to_email = form.cleaned_data.get("email")
            
            send_mail(
                mail_subject,
                message,
                'noreply@rebootverde.com',
                [to_email],
                fail_silently=False,
            )

            
            request.session['verification_email'] = to_email
            return redirect('verify_code')
    else:
        form = RegistrationForm()

    return render(request, "registration/register.html", {"form": form})


def verify_code(request):
    email = request.session.get('verification_email')
    
    if not email:
        return redirect('register')

    if request.method == "POST":
        digitado = request.POST.get('code')
        try:
            
            user = User.objects.get(email=email, verification_code=digitado)
            user.is_verified = True
            user.verification_code = None  
            user.save()
            
            
            del request.session['verification_email']
            
            
            return render(request, "users/register_success.html")
            
        except User.DoesNotExist:
            
            messages.error(request, "Código errado")
    
    return render(request, "users/verify_code.html", {"email": email})


@login_required
def shop(request):
    return render(request, "users/shop.html")
