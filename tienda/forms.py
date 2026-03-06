from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.utils.safestring import mark_safe
from django.core.exceptions import ValidationError
import re


def validate_username_letters_only(value):
    """Validador que solo acepta letras en el nombre de usuario"""
    if not value.isalpha():
        raise ValidationError(
            'El nombre de usuario solo puede contener letras (sin números ni caracteres especiales).',
            code='invalid_username',
        )
    if len(value) < 3:
        raise ValidationError(
            'El nombre de usuario debe tener al menos 3 letras.',
            code='too_short',
        )


class EmailUserCreationForm(UserCreationForm):
    username = forms.CharField(
        label='Nombre de usuario',
        required=True,
        validators=[validate_username_letters_only],
        widget=forms.TextInput(attrs={
            'placeholder': 'ej: juanperez',
            'class': 'form-input'
        }),
        help_text='Solo letras, sin números ni caracteres especiales. Mínimo 3 letras.'
    )
    email = forms.EmailField(
        label='Correo electrónico',
        widget=forms.EmailInput(attrs={
            'placeholder': 'tu@email.com',
            'class': 'form-input'
        })
    )
    first_name = forms.CharField(
        label='Nombre completo',
        required=False,
        widget=forms.TextInput(attrs={
            'placeholder': 'Juan Pérez',
            'class': 'form-input'
        }),
        help_text='Opcional'
    )
    password1 = forms.CharField(
        label='Contraseña',
        widget=forms.PasswordInput(attrs={
            'id': 'id_password1',
            'class': 'password-input',
            'autocomplete': 'new-password',
            'placeholder': 'Escribe tu contraseña'
        })
    )
    password2 = forms.CharField(
        label='Confirmar contraseña',
        widget=forms.PasswordInput(attrs={
            'id': 'id_password2',
            'class': 'password-input',
            'autocomplete': 'new-password',
            'placeholder': 'Repite tu contraseña'
        })
    )

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username', 'email', 'first_name', 'password1', 'password2')

    def save(self, commit: bool = True) -> User:
        user = super().save(commit=False)
        # assign email from the form
        email = self.cleaned_data.get('email')
        first_name = self.cleaned_data.get('first_name')
        if email:
            user.email = email
        if first_name:
            user.first_name = first_name
        if commit:
            user.save()
        return user

    def clean(self):
        cleaned = super().clean()
        email = cleaned.get('email')
        username = cleaned.get('username')
        
        if not email:
            raise ValidationError('El correo electrónico es obligatorio para registrarse.')
        
        if not username:
            raise ValidationError('El nombre de usuario es obligatorio.')

        return cleaned


class EmailAuthenticationForm(AuthenticationForm):
    """Authentication form that asks for username."""
    username = forms.CharField(
        label='Nombre de usuario',
        max_length=30,
        widget=forms.TextInput(attrs={
            'maxlength': '30',
            'placeholder': 'Tu nombre de usuario',
            'class': 'form-input'
        })
    )
    password = forms.CharField(
        label='Contraseña',
        strip=False,
        widget=forms.PasswordInput(attrs={
            'id': 'id_password',
            'class': 'password-input',
            'placeholder': 'Tu contraseña',
            'autocomplete': 'current-password'
        })
    )
