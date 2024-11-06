from django import forms
from .models import *
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.contrib.auth import authenticate
from django.core.exceptions import ValidationError


class UserRegistrationForm(forms.ModelForm):
    phone_number = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Номер телефона', 'type': 'tel', 'value': '+375'}))
    first_name = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'placeholder': 'Имя'}))
    last_name = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'placeholder': 'Фамилия'}))
    email = forms.EmailField(widget=forms.EmailInput(attrs={'placeholder': 'Почта'})) 
    password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Введите пароль'}))
    confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Повторите пароль'})) 

    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'phone_number', 'email', 'password', 'confirm_password'] 
        labels = {
            'first_name': 'Имя', 
            'last_name': 'Фамилия', 
            'phone_number': 'Номер телефона', 
            'email': 'Электронная почта', 
            'password': 'Пароль'
        }
    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')

        if password != confirm_password:
            raise forms.ValidationError("Пароли не совпадают")
        return cleaned_data
    

class LoginForm(forms.Form):
    identifier = forms.CharField(widget=forms.TextInput(attrs={
        'placeholder': 'Номер телефона или Email'
    }))
    login_password = forms.CharField(widget=forms.PasswordInput(attrs={
        'placeholder': 'Пароль'
    }))

class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ('email', 'phone_number')

class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = CustomUser
        fields = ('email', 'phone_number')

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'email', 'phone_number', 'avatar']
        labels = {
            'first_name': 'Имя', 
            'last_name': 'Фамилия', 
            'phone_number': 'Номер телефона', 
            'email': 'Электронная почта', 
            'avatar': 'Фото профиля'
        }
    def __init__(self, *args, **kwargs):
        super(UserProfileForm, self).__init__(*args, **kwargs)
        self.fields['first_name'].widget.attrs.update({'class': 'form-control'})
        self.fields['last_name'].widget.attrs.update({'class': 'form-control'})
        self.fields['email'].widget.attrs.update({'class': 'form-control'})
        self.fields['phone_number'].widget.attrs.update({'class': 'form-control'})
        self.fields['avatar'].widget.attrs.update({'class': 'form-control-file'})   