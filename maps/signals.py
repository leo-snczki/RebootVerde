from django.db.models.signals import post_save, post_migrate
from django.contrib.auth.models import Group, Permission
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
        
@receiver(post_migrate)
def create_groups(sender, **kwargs):
    owner_group, _ = Group.objects.get_or_create(name="Owner")
    user_group, _ = Group.objects.get_or_create(name="User")

    perms = Permission.objects.filter(
        codename__in=[
            "add_ewastepin",
            "change_ewastepin",
            "delete_ewastepin",
            "view_ewastepin",

            "add_ewastepinopeninghours",
            "change_ewastepinopeninghours",
            "delete_ewastepinopeninghours",
            "view_ewastepinopeninghours",

            "add_recyclingcode",
            "change_recyclingcode",
            "delete_recyclingcode",
            "view_recyclingcode",
        ]
    )

    owner_group.permissions.set(perms)
    user_group.permissions.clear()        