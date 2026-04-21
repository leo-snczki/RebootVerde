from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.contrib.auth import get_user_model
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from .models import EwastePin

User = get_user_model()

@receiver(post_save, sender=EwastePin)
def notify_users_new_pin(sender, instance, created, **kwargs):
    if created:
        users_emails = list(User.objects.filter(
            is_active=True, 
            receive_newsletter=True
        ).values_list('email', flat=True))
        
        if users_emails:
            subject = '🌍 Novo Ponto de Coleta: ' + (instance.name or "Disponível no Mapa")
            
            context = {
                'pin': instance,
                'domain': 'rebootverde.com', # o site nao existe mas esse tá bom
            }
            
            # Renderiza o HTML
            html_message = render_to_string('maps/emails/new_pin_notification.html', context)
            
            plain_message = strip_tags(html_message)
            
            send_mail(
                subject,
                plain_message,
                'rebootverde123@gmail.com',
                users_emails,
                html_message=html_message,
                fail_silently=True,
            )