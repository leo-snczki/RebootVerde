from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import get_user_model, login
from django.core.mail import send_mail
from django.urls import reverse
from django.contrib.auth.views import LoginView
from .forms import RegistrationForm, EmailChangeForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import login_required
from shop.models import Order

from django.contrib.auth.forms import SetPasswordForm, PasswordResetForm
from .forms import RegistrationForm, EmailChangeForm, PasswordResetCodeForm

User = get_user_model()

class CustomLoginView(LoginView):
    template_name = "registration/login.html"

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
            
            
            html_message = f"""
            <div style="font-family: Arial, sans-serif; background-color: #f4f4f4; padding: 40px; text-align: center;">
                <div style="max-width: 500px; margin: 0 auto; background-color: #ffffff; border-radius: 15px; overflow: hidden; box-shadow: 0 4px 10px rgba(0,0,0,0.1);">
                    <div style="background-color: #1b4332; padding: 25px; color: #ffffff;">
                        <h1 style="margin: 0; font-size: 24px; letter-spacing: 2px;">
                            <span style="color: #52b788;">///</span> REBOOTVERDE <span style="color: #52b788;">///</span>
                        </h1>
                    </div>
                    <div style="padding: 30px; color: #333333;">
                        <h2 style="color: #1b4332;">Olá, {user.username}!</h2>
                        <p style="font-size: 16px; line-height: 1.5;">Obrigado por se juntar à nossa missão verde. Use o código abaixo para validar sua conta:</p>
                        <div style="background-color: #f0fdf4; border: 2px dashed #1b4332; padding: 20px; margin: 25px 0; border-radius: 10px;">
                            <span style="font-size: 32px; font-weight: bold; color: #1b4332; letter-spacing: 5px;">{code}</span>
                        </div>
                        <p style="font-size: 13px; color: #888888;">Se você não solicitou este registro, ignore este e-mail.</p>
                    </div>
                    <div style="background-color: #f8f9fa; padding: 15px; font-size: 12px; color: #999999;">
                        &copy; 2026 RebootVerde 
                </div>
            </div>
            """
            
            
            plain_message = f"Olá {user.username}, seu código de verificação é: {code}"
            
            to_email = form.cleaned_data.get("email")
            
            send_mail(
                mail_subject,
                plain_message,
                'noreply@rebootverde.com',
                [to_email],
                html_message=html_message,
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
def profile(request):
    return render(request, "users/profile.html")

@login_required
def change_email(request):
    if request.method == 'POST':
        form = EmailChangeForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'O seu email foi atualizado com sucesso!')
            return redirect('profile')
    else:
        form = EmailChangeForm(instance=request.user)
    
    return render(request, 'users/change_email.html', {'form': form})

@login_required
def delete_account(request):
    if request.method == 'POST':
        user = request.user
        user.delete()
        messages.success(request, 'A sua conta foi eliminada com sucesso.')
        return redirect('index')
    
    return render(request, 'users/delete_account_confirm.html')


def password_reset_request(request):
    if request.method == "POST":
        form = PasswordResetForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            user = User.objects.filter(email=email).first()
            if user:
                code = user.generate_verification_code()
                
                mail_subject = "Código de Recuperação - RebootVerde"
                html_message = f"""
                <div style="font-family: Arial; text-align: center;">
                    <h2>Recuperação de Senha</h2>
                    <p>Use o código abaixo para redefinir sua senha:</p>
                    <div style="font-size: 32px; font-weight: bold; color: #1b4332; border: 2px dashed #1b4332; padding: 10px;">{code}</div>
                </div>
                """
                send_mail(mail_subject, f"Código: {code}", 'noreply@rebootverde.com', [email], html_message=html_message)
                request.session['reset_email'] = email
                return redirect('password_reset_verify')
    else:
        form = PasswordResetForm()
    return render(request, "users/password_reset_form.html", {"form": form})

from django.shortcuts import render, redirect
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import SetPasswordForm
from django.contrib import messages

User = get_user_model()

def password_reset_verify(request):
    email = request.session.get('reset_email')
    if not email:
        return redirect('password_reset')

    if request.method == 'POST':
        form = PasswordResetCodeForm(request.POST)
        if form.is_valid():
            
            request.session['reset_authorized'] = True
            return redirect('password_reset_new_password')
    else:
        form = PasswordResetCodeForm(initial={'email': email})

    return render(request, 'users/password_reset_verify.html', {'form': form})

def password_reset_new_password(request):
    email = request.session.get('reset_email')
    authorized = request.session.get('reset_authorized')

    
    if not email or not authorized:
        messages.error(request, "Sessão expirada ou não autorizada.")
        return redirect('password_reset')

    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        return redirect('password_reset')

    if request.method == 'POST':
        form = SetPasswordForm(user, request.POST)
        if form.is_valid():
            form.save()
            
            del request.session['reset_email']
            del request.session['reset_authorized']
            
            
            user.verification_code = ""
            user.save()
            
            messages.success(request, "Senha alterada com sucesso!")
            return redirect('password_reset_complete')
    else:
        form = SetPasswordForm(user)

    return render(request, 'users/password_reset_new_password.html', {'form': form})


@login_required
def profile(request):
    
    orders = Order.objects.filter(user=request.user).order_by('-created')
    
    return render(request, 'users/profile.html', {
        'orders': orders
    })