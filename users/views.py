import base64
from io import BytesIO
import qrcode

from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import get_user_model, login
from django.urls import reverse
from django.contrib.auth.views import LoginView
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import SetPasswordForm, PasswordResetForm

from django_otp import verify_token
from django_otp.plugins.otp_totp.models import TOTPDevice


from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm
from shop.models import Order

from .forms import RegistrationForm, EmailChangeForm, PasswordResetCodeForm, RedeemCodeForm
from shop.models import Order
from users.models import UserPoints
from .services import redeem_code, send_verification_email
from django.core.mail import send_mail

User = get_user_model()

class CustomLoginView(LoginView):
    template_name = "registration/login.html"

    def form_valid(self, form):
        user = form.get_user()

        if not user.email_verified:
            code = user.generate_verification_code()
            send_verification_email(user, code)

            self.request.session['verification_email'] = user.email
            return redirect('verify_code')

        if user.two_factor_enabled:
            self.request.session['pending_2fa_user_id'] = user.id
            return redirect('verify_2fa')

        login(self.request, user)
        return redirect('index')

def verify_2fa(request):
    user_id = request.session.get('pending_2fa_user_id')
    if not user_id:
        return redirect('login')

    try:
        user = User.objects.get(id=user_id)
        device, _ = TOTPDevice.objects.get_or_create(user=user, name="Default")
    except Exception:
        return redirect('login')

    is_new_device = not user.two_factor_enabled

    if request.method == 'POST':
        token = request.POST.get('token')

        if device.verify_token(token):
            if not user.two_factor_enabled:
                user.two_factor_enabled = True
                user.save()

            login(request, user)
            request.session.pop('pending_2fa_user_id', None)
            return redirect('index')
        else:
            messages.error(request, "Código inválido.")

    qr_code_base64 = None
    if is_new_device:
        url = device.config_url
        img = qrcode.make(url)
        buffer = BytesIO()
        img.save(buffer, format="PNG")
        qr_code_base64 = base64.b64encode(buffer.getvalue()).decode()

    return render(request, 'users/verify_2fa.html', {
        'qr_code': qr_code_base64,
        'is_new_device': is_new_device
    })

    qr_code_base64 = None
    if is_new_device:
        url = device.config_url
        img = qrcode.make(url)
        buffer = BytesIO()
        img.save(buffer, format="PNG")
        qr_code_base64 = base64.b64encode(buffer.getvalue()).decode()

    return render(request, 'users/verify_2fa.html', {
        'qr_code': qr_code_base64,
        'is_new_device': is_new_device
    })

def register_user(request):
    if request.method == "POST":
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = True  
            user.email_verified = False 
            user.save()

            code = user.generate_verification_code()    

            send_verification_email(user, code)

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
            user.email_verified = True
            user.verification_code = None  
            user.save()
            del request.session['verification_email']
            return render(request, "users/register_success.html")
        except User.DoesNotExist:
            messages.error(request, "Código errado")
    
    return render(request, "users/verify_code.html", {"email": email})

@login_required
def profile(request):
    orders = Order.objects.filter(user=request.user).order_by('-created')
    points_obj, _ = UserPoints.objects.get_or_create(user=request.user)

    is_owner = request.user.groups.filter(name="Owner").exists()
    is_staff = request.user.is_staff
    is_superuser = request.user.is_superuser

    return render(request, 'users/profile.html', {
        'orders': orders,
        'points': points_obj.points,
        'is_owner': is_owner,
        'is_staff': is_staff,
        'is_superuser': is_superuser,
    })

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
        request.user.delete()
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
                <div style="font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #f4f7f6; padding: 40px 10px; color: #333;">
                    <div style="max-width: 500px; margin: 0 auto; background-color: #ffffff; border-radius: 8px; overflow: hidden; box-shadow: 0 4px 10px rgba(0,0,0,0.1);">
                        
                        <div style="background-color: #2d6a4f; padding: 20px; text-align: center;">
                            <h1 style="color: #ffffff; margin: 0; font-size: 24px; letter-spacing: 1px;">RebootVerde</h1>
                        </div>

                        <div style="padding: 30px; text-align: center;">
                            <h2 style="color: #2d6a4f; margin-bottom: 10px;">Recuperação de Senha</h2>
                            <p style="font-size: 16px; color: #666; line-height: 1.5;">
                                Olá! Recebemos uma solicitação para redefinir sua senha. 
                                Use o código abaixo para prosseguir com a verificação:
                            </p>
                            
                            <div style="margin: 30px 0; padding: 20px; background-color: #f0fdf4; border: 2px dashed #2d6a4f; border-radius: 10px;">
                                <span style="font-size: 32px; font-weight: bold; color: #1b4332; letter-spacing: 5px;">{code}</span>
                            </div>

                            <p style="font-size: 14px; color: #999; margin-top: 20px;">
                                Este código expira em breve. Se você não solicitou esta alteração, ignore este e-mail.
                            </p>
                        </div>

                        <div style="background-color: #f9f9f9; padding: 15px; text-align: center; border-top: 1px solid #eeeeee;">
                            <p style="font-size: 12px; color: #aaa; margin: 0;">
                                &copy; 2026 RebootVerde. Todos os direitos reservados.
                            </p>
                        </div>
                    </div>
                </div>
                """
                send_mail(mail_subject, f"Código: {code}", 'rebootverde123@gmail.com', [email], html_message=html_message)
                request.session['reset_email'] = email
                return redirect('password_reset_verify')
    else:
        form = PasswordResetForm()
    return render(request, "users/password_reset_form.html", {"form": form})

def password_reset_verify(request):
    email = request.session.get('reset_email')
    if not email: return redirect('password_reset')

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
        return redirect('password_reset')

    user = User.objects.get(email=email)
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
def unsubscribe_newsletter(request):
    request.user.receive_newsletter = False
    request.user.save()
    messages.success(request, "Subscrição cancelada.")
    return redirect('profile')

@login_required
def subscribe_newsletter(request):
    request.user.receive_newsletter = True
    request.user.save()
    messages.success(request, "Subscrição ativada.")
    return redirect('profile')

@login_required
def redeem_code_view(request):
    if request.method == "POST":
        form = RedeemCodeForm(request.POST)

        if form.is_valid():
            code = form.cleaned_data["code"]

            try:
                redeem_code(request.user, code)
                messages.success(request, "Código resgatado com sucesso!")
                return redirect("redeem_code")

            except Exception as e:
                messages.error(request, str(e))
    else:
        form = RedeemCodeForm()

    return render(request, "users/redeem_code.html", {
        "form": form
    })
    



@login_required
def order_invoice(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="fatura_{order.id}.pdf"'

    c = canvas.Canvas(response, pagesize=A4)
    width, height = A4
    
   
    verde_destaque = colors.HexColor("#000000")
    preto_suave = colors.HexColor("#2d2d2d")
    cinza_claro = colors.HexColor("#f8f8f8")
    cinza_texto = colors.HexColor("#555555")

    
    c.setFillColor(cinza_claro)
    c.rect(0, height - 4*cm, width, 4*cm, fill=1, stroke=0)
    
    
    c.setFillColor(verde_destaque)
    c.setFont("Helvetica-Bold", 26)
    c.drawString(1.5*cm, height - 2.2*cm, "REBOOTVERDE")
    
    c.setFillColor(preto_suave)
    c.setFont("Helvetica", 9)
    c.drawString(1.5*cm, height - 2.8*cm, "SOLUÇÕES SUSTENTÁVEIS E TECNOLOGIA")

    
    c.setFont("Helvetica-Bold", 10)
    c.drawRightString(width - 1.5*cm, height - 1.8*cm, f"FATURA Nº: #INV-{order.id}")
    c.setFont("Helvetica", 9)
    c.setFillColor(cinza_texto)
    c.drawRightString(width - 1.5*cm, height - 2.3*cm, f"Emitido em: {order.created.strftime('%d/%m/%Y %H:%M')}")
    c.drawRightString(width - 1.5*cm, height - 2.7*cm, f"Estado: {'CONFIRMADO' if order.paid else 'AGUARDA PAGAMENTO'}")

    
    c.setStrokeColor(colors.black)
    c.setLineWidth(1)
    c.line(1.5*cm, height - 4.5*cm, width - 1.5*cm, height - 4.5*cm)

    
    y = height - 5.5*cm
    
    # Estilo dos Rótulos
    c.setFillColor(verde_destaque)
    c.setFont("Helvetica-Bold", 8)
    c.drawString(1.5*cm, y, "DADOS DE FATURAÇÃO")
    c.drawString(10.5*cm, y, "DETALHES DE ENTREGA")

    
    c.setFillColor(preto_suave)
    c.setFont("Helvetica", 10)
    c.drawString(1.5*cm, y - 0.6*cm, f"{order.first_name} {order.last_name}")
    c.setFont("Helvetica", 9)
    c.drawString(1.5*cm, y - 1.1*cm, f"NIF: {order.nif if order.nif else 'Consumidor Final'}")
    c.drawString(1.5*cm, y - 1.6*cm, f"Email: {order.email}")

    c.setFont("Helvetica", 10)
    c.drawString(10.5*cm, y - 0.6*cm, f"{order.address}")
    c.setFont("Helvetica", 9)
    c.drawString(10.5*cm, y - 1.1*cm, f"{order.postal_code}, {order.city}")

    
    y_table = y - 3.5*cm
    
    
    c.setFillColor(preto_suave)
    c.setFont("Helvetica-Bold", 9)
    c.drawString(1.5*cm, y_table, "DESCRIÇÃO DO ARTIGO")
    c.drawCentredString(width - 6*cm, y_table, "QTD")
    c.drawRightString(width - 4*cm, y_table, "P. UNIT")
    c.drawRightString(width - 1.5*cm, y_table, "TOTAL")

    
    c.setLineWidth(0.5)
    c.line(1.5*cm, y_table - 0.2*cm, width - 1.5*cm, y_table - 0.2*cm)

    
    current_y = y_table - 0.8*cm
    c.setFont("Helvetica", 9)
    
    for item in order.items.all():
        if current_y < 4*cm:
            c.showPage()
            current_y = height - 3*cm

       
        c.setFillColor(preto_suave)
        c.setFont("Helvetica-Bold", 9)
        c.drawString(1.5*cm, current_y, item.product.name.upper())
        

        c.setFillColor(cinza_texto)
        c.setFont("Helvetica-Oblique", 8)
        c.drawString(1.5*cm, current_y - 0.4*cm, f"Categoria: {item.product.category.name}")


        c.setFillColor(preto_suave)
        c.setFont("Helvetica", 9)
        c.drawCentredString(width - 6*cm, current_y, str(item.quantity))
        c.drawRightString(width - 4*cm, current_y, f"{item.price} PRV")
        c.drawRightString(width - 1.5*cm, current_y, f"{item.get_cost()} PRV")
        

        c.setDash(1, 2)
        c.line(1.5*cm, current_y - 0.7*cm, width - 1.5*cm, current_y - 0.7*cm)
        c.setDash()
        
        current_y -= 1.2*cm


    current_y -= 0.5*cm
    c.setLineWidth(1)
    c.line(width - 7*cm, current_y, width - 1.5*cm, current_y)
    
    current_y -= 0.6*cm
    c.setFont("Helvetica", 10)
    c.drawString(width - 7*cm, current_y, "SUBTOTAL")
    c.drawRightString(width - 1.5*cm, current_y, f"{order.get_total_cost()} PRV")
    
    current_y -= 0.6*cm
    c.setFillColor(verde_destaque)
    c.setFont("Helvetica-Bold", 14)
    c.drawString(width - 7*cm, current_y, "TOTAL")
    c.drawRightString(width - 1.5*cm, current_y, f"{order.get_total_cost()} PRV")


    c.setFillColor(cinza_texto)
    c.setFont("Helvetica", 7)
    footer_text = "RebootVerde - Comércio Eletrónico de Produtos Sustentáveis | www.rebootverde.com"
    c.drawCentredString(width/2, 2*cm, footer_text)
    c.drawCentredString(width/2, 1.6*cm, "Este documento serve como comprovativo de compra.")

    c.showPage()
    c.save()
    return response

def resend_verification_code(request):
    email = request.session.get('verification_email')
    if not email:
        return redirect('login')

    try:
        user = User.objects.get(email=email)

        code = user.generate_verification_code()
        send_verification_email(user, code)

        messages.success(request, "Novo código enviado para o seu email.")

    except User.DoesNotExist:
        messages.error(request, "Utilizador não encontrado.")

    return redirect('verify_code')
