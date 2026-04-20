#https://youtu.be/kuwjPcmc88U?si=xys5bABOEpxJTaMV
from django.shortcuts import render
from django.core.mail import send_mail
from django.conf import settings

def index(request):
    return render(request, 'index.html')

def about(request):
    return render(request, 'about.html')

def game_view(request):
    return render(request, 'game.html')
# def contact_view(request):
#     return render(request, 'contact.html')



def contact_view(request):
    if request.method == 'POST':
        
        name = request.POST.get('name')
        user_email = request.POST.get('email')
        subject = request.POST.get('subject')
        mensagem = request.POST.get('mensagem')

        # Montando o corpo do e-mail
        corpo_email = f"Mensagem de: {name} <{user_email}>\n\n{mensagem}"

        # Enviando o e-mail
        send_mail(
            f"Contato Site: {subject}", 
            corpo_email,                
            settings.EMAIL_HOST_USER,   
            [settings.EMAIL_HOST_USER], 
            fail_silently=False,
        )

        return render(request, 'contact_success.html') 
    return render(request, 'contact.html')
