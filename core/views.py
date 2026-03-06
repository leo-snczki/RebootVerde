#https://youtu.be/kuwjPcmc88U?si=xys5bABOEpxJTaMV
from django.shortcuts import render
from django.core.mail import send_mail
from django.conf import settings

def index(request):
    return render(request, 'index.html')

def about(request):
    return render(request, 'about.html')

# def contact_view(request):
#     return render(request, 'contact.html')



def contact_view(request):
    if request.method == 'POST':
        # Pegando os dados do formulário (os nomes 'nome', 'email', etc., devem bater com o 'name' no HTML)
        nome = request.POST.get('nome')
        email_usuario = request.POST.get('email')
        assunto = request.POST.get('assunto')
        mensagem = request.POST.get('mensagem')

        # Montando o corpo do e-mail
        corpo_email = f"Mensagem de: {nome} <{email_usuario}>\n\n{mensagem}"

        # Enviando o e-mail
        send_mail(
            f"Contato Site: {assunto}", # Assunto
            corpo_email,                # Mensagem
            settings.EMAIL_HOST_USER,   # De: (Seu e-mail configurado no settings)
            [settings.EMAIL_HOST_USER], # Para: (Onde você quer receber o e-mail)
            fail_silently=False,
        )

        return render(request, 'contact_success.html') # Redireciona para o sucesso

    return render(request, 'contact.html')