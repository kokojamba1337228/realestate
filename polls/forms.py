from django import forms
from .models import *

class UserRegistrationForm(forms.ModelForm):
    phone_number = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Номер телефона'}))
    first_name = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'placeholder': 'Имя'}))
    last_name = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'placeholder': 'Фамилия'}))
    email = forms.EmailField(widget=forms.EmailInput(attrs={'placeholder': 'Почта'}))  # Ensure email field is included
    password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Введите пароль'}))
    confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Повторите пароль'}))  # Add confirm password field

    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'phone_number', 'email', 'password', 'confirm_password']  # Include the new field

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')

        if password != confirm_password:
            raise forms.ValidationError("Пароли не совпадают")
            self.add_error('confirm_password', "Passwords do not match.")
        return cleaned_data