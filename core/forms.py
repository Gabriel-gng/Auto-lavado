import re
from django import forms
from django.contrib.auth.models import User
from .models import PerfilUsuario, Vehiculo


class LoginForm(forms.Form):
    username = forms.CharField(
        label='Correo Electrónico o usuario',
        widget=forms.TextInput(attrs={
            'class': 'form-control form-control-lg',
            'placeholder': ''
        })
    )
    password = forms.CharField(
        label='Contraseña',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control form-control-lg',
            'placeholder': ''
        })
    )


class ActualizarPerfilForm(forms.Form):
    nombre_completo = forms.CharField(
        label='Nombre Completo',
        max_length=150,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    documento_identidad = forms.CharField(
        label='Documento de Identidad',
        max_length=20,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    telefono = forms.CharField(
        label='Teléfono (10 dígitos)',
        max_length=10,
        min_length=10,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    email = forms.EmailField(
        label='Correo Electrónico',
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )

    def clean_telefono(self):
        telefono = self.cleaned_data.get('telefono', '')
        if not telefono.isdigit():
            raise forms.ValidationError('El teléfono solo debe contener números.')
        if len(telefono) != 10:
            raise forms.ValidationError('El teléfono debe tener exactamente 10 dígitos.')
        return telefono


class RegistroUsuarioForm(forms.Form):
    nombre_completo = forms.CharField(
        label='Nombre Completo',
        max_length=150,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    documento_identidad = forms.CharField(
        label='Documento de Identidad',
        max_length=20,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    telefono = forms.CharField(
        label='Teléfono (10 dígitos)',
        max_length=10,
        min_length=10,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )

    def clean_telefono(self):
        telefono = self.cleaned_data.get('telefono', '')
        if not telefono.isdigit():
            raise forms.ValidationError('El teléfono solo debe contener números.')
        if len(telefono) != 10:
            raise forms.ValidationError('El teléfono debe tener exactamente 10 dígitos.')
        return telefono
    email = forms.EmailField(
        label='Correo Electrónico',
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )
    password = forms.CharField(
        label='Contraseña',
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )
    password_confirm = forms.CharField(
        label='Confirmar Contraseña',
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        password_confirm = cleaned_data.get('password_confirm')
        if password and password_confirm and password != password_confirm:
            raise forms.ValidationError('Las contraseñas no coinciden.')
        return cleaned_data

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('Este correo ya está registrado.')
        return email


class VehiculoForm(forms.ModelForm):
    class Meta:
        model = Vehiculo
        fields = ['tipo', 'placa', 'marca', 'modelo', 'color']
        widgets = {
            'tipo': forms.Select(attrs={'class': 'form-control'}, choices=[
                ('', 'Seleccionar'),
                ('Moto', 'Moto'),
                ('Carro', 'Carro'),
                ('Camioneta', 'Camioneta'),
            ]),
            'placa': forms.TextInput(attrs={'class': 'form-control'}),
            'marca': forms.TextInput(attrs={'class': 'form-control'}),
            'modelo': forms.TextInput(attrs={'class': 'form-control'}),
            'color': forms.TextInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'tipo': 'Tipo de Vehículo',
            'placa': 'Placa',
            'marca': 'Marca',
            'modelo': 'Modelo',
            'color': 'Color',
        }

    def clean_placa(self):
        placa = self.cleaned_data.get('placa', '').upper().strip()
        tipo = self.cleaned_data.get('tipo')

        if tipo == 'Moto':
            # Moto: 3 letras + 2 números + 1 letra (ej: ABC12D)
            if not re.match(r'^[A-Z]{3}[0-9]{2}[A-Z]$', placa):
                raise forms.ValidationError(
                    'La placa de moto debe tener 3 letras, 2 números y 1 letra en el siguiente orden (ej: ABC12D).'
                )
        elif tipo in ('Carro', 'Camioneta'):
            # Carro/Camioneta: 3 letras + 3 números (ej: ABC123)
            if not re.match(r'^[A-Z]{3}[0-9]{3}$', placa):
                raise forms.ValidationError(
                    'La placa de carro debe tener 3 letras y 3 números en el siguiente orden (ej: ABC123).'
                )

        return placa
