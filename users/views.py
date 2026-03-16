# https://www.youtube.com/watch?v=DIFaOkxy6TE
# https://www.youtube.com/watch?v=vzBFJ3WEvOQ
from django.shortcuts import render
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login
from .forms import FormularioRegistroCompleto

def register_view(request):  
    if request.method == 'POST':  
        form = form = FormularioRegistroCompleto(request.POST)
        if form.is_valid():  
            form.save()
            # login(request, form.save()) # loga o user automaticamente após o registro, mas tenho de ver como confirma o email primeiro, então não vou usar isso agora
            return render(request, 'users/register_success.html')  
    else:  
        form = FormularioRegistroCompleto
    return render(request, 'users/register.html', {'form': form}) # ta no video

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            login(request, form.get_user())
            return render(request, 'users/login_success.html')
    else:
        form = AuthenticationForm()
    return render(request, 'users/login.html', {'form': form})