from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model

User = get_user_model()

def validate_nif_pt(value):
    nif = str(value)
    if not nif.isdigit() or len(nif) != 9:
        raise ValidationError("NIF must have exactly 9 digits.")
    
    if nif[0] not in '123456789':
        raise ValidationError("Invalid NIF prefix.")

    soma = sum(int(nif[i]) * (9 - i) for i in range(8))
    resto = soma % 11
    check_digit = 0 if resto < 2 else 11 - resto

    if int(nif[8]) != check_digit:
        raise ValidationError("The NIF provided is not valid.")

class RegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    nif = forms.CharField(
        required=True, 
        max_length=9, 
        min_length=9,
        validators=[validate_nif_pt]
    )

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("username", "email", "nif")

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if User.objects.filter(email=email).exists():
            raise ValidationError("An account with this email address already exists!")
        return email

    def clean_nif(self):
        nif = self.cleaned_data.get("nif")
        if User.objects.filter(nif=nif).exists():
            raise ValidationError("This NIF is already registered.")
        return nif

class EmailChangeForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['email']

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exclude(pk=self.instance.pk).exists():
            raise ValidationError("An account with this email address already exists!")
        return email

class PasswordResetCodeForm(forms.Form):
    email = forms.EmailField(label="Email")
    code = forms.CharField(max_length=6, label="6-digit Code")

    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get("email")
        code = cleaned_data.get("code")
        
        if email and code:
            if not User.objects.filter(email=email, verification_code=code).exists():
                raise ValidationError("Invalid email or verification code.")
        return cleaned_data

class RedeemCodeForm(forms.Form):
    code = forms.CharField(
        max_length=12,
        label="",
        widget=forms.TextInput(attrs={
            "placeholder": "Inserir código",
            "class": "form-control form-control-lg text-center"
        })
    )