from django.shortcuts import get_object_or_404
from django.utils import timezone
from maps.models import RecyclingCode, RedemptionLog
from .models import UserPoints
from django.core.mail import send_mail


def redeem_code(user, code_str):
    code = get_object_or_404(RecyclingCode, code=code_str)

    if code.is_used:
        raise ValueError("Código já utilizado")

    if code.created_by == user:
        raise ValueError("Não podes usar o teu próprio código")

    code.is_used = True
    code.used_by = user
    code.used_at = timezone.now()
    code.save()

    wallet, _ = UserPoints.objects.get_or_create(user=user)
    wallet.add_points(code.points)

    # log
    RedemptionLog.objects.create(
        user=user,
        code=code,
        points_earned=code.points
    )

    return wallet.points

def send_verification_email(user, code):
    subject = "Código de ativação - RebootVerde"

    html_message = f"""
    <div style="font-family: Arial, sans-serif; background-color: #f4f4f4; padding: 40px; text-align: center;">
        <div style="max-width: 500px; margin: 0 auto; background-color: #ffffff; border-radius: 15px; box-shadow: 0 4px 10px rgba(0,0,0,0.1);">
            <div style="background-color: #1b4332; padding: 25px; color: #ffffff;">
                <h1 style="margin: 0; font-size: 24px;">REBOOTVERDE</h1>
            </div>
            <div style="padding: 30px; color: #333333;">
                <h2>Olá, {user.username}!</h2>
                <p>Use o código abaixo para validar a sua conta:</p>
                <div style="background-color: #f0fdf4; border: 2px dashed #1b4332; padding: 20px; margin: 25px 0;">
                    <span style="font-size: 32px; font-weight: bold; color: #1b4332; letter-spacing: 5px;">
                        {code}
                    </span>
                </div>
            </div>
        </div>
    </div>
    """

    plain_message = f"O seu código de verificação é: {code}"

    send_mail(
        subject,
        plain_message,
        "rebootverde123@gmail.com",
        [user.email],
        html_message=html_message
    )