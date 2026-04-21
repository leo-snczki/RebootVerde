from django import forms
from .models import Order
from users.forms import validate_nif_pt  

class OrderCreateForm(forms.ModelForm):
    nif = forms.CharField(
        label="NIF",
        max_length=9,
        min_length=9,
        validators=[validate_nif_pt],
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'NIF (9 dígitos)'})
    )

    class Meta:
        model = Order
        fields = ['first_name', 'last_name', 'email', 'nif', 'address', 'postal_code', 'city']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nome'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Apelido'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'}),
            'address': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Morada'}),
            'postal_code': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Código Postal'}),
            'city': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Cidade'}),
        }