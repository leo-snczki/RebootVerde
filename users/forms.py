from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model


User = get_user_model()

class RegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)


    class Meta(UserCreationForm.Meta):
        model = User
        class RegistrationForm(UserCreationForm):
            email = forms.EmailField(required=True)
        nif = forms.CharField(required=True, max_length=9)  

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("username", "email", "nif") 

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if User.objects.filter(email=email).exists():
            raise ValidationError("An account with this email address already exists!")
        return email

class EmailChangeForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['email']

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exclude(pk=self.instance.pk).exists():
            raise ValidationError("An account with this email address already exists!")
        return email
    

from django.contrib.auth.forms import SetPasswordForm

class PasswordResetCodeForm(forms.Form):
    email = forms.EmailField(label="Email")
    code = forms.CharField(max_length=6, label="Código de 6 dígitos")

    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get("email")
        code = cleaned_data.get("code")
        
        if email and code:
            if not User.objects.filter(email=email, verification_code=code).exists():
                raise ValidationError("Email ou código inválidos.")
        return cleaned_data
    


class PasswordResetCodeForm(forms.Form):
    email = forms.EmailField(label="Email")
    code = forms.CharField(max_length=6, label="Código de 6 dígitos")

    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get("email")
        code = cleaned_data.get("code")
        
        if email and code:
            
            if not User.objects.filter(email=email, verification_code=code).exists():
                raise ValidationError("Email ou código inválidos.")
        return cleaned_data