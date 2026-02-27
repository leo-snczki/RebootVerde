# https://www.youtube.com/watch?v=DIFaOkxy6TE
from django.shortcuts import render
from django.contrib.auth.forms import UserCreationForm

def register_view(request):  
    if request.method == 'POST':  
        form = UserCreationForm(request.POST)  
        if form.is_valid():  
            form.save()  
            return render(request, 'users/register_success.html')  
    else:  
        form = UserCreationForm() # tá no video  
    return render(request, 'users/register.html', {'form': form}) # ta no video