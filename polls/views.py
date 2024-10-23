from django.shortcuts import render, redirect
from .forms import UserRegistrationForm
from django.contrib.auth import login, authenticate
from django.contrib import messages
from django.contrib.auth import get_user_model
from .forms import LoginForm

User = get_user_model()

def user_register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            
            user.set_password(form.cleaned_data['password'])
            
            user.save()
            
            user = authenticate(email=form.cleaned_data['email'], password=form.cleaned_data['password'])
            if user is not None:
                login(request, user)
                messages.success(request, f'Ваш аккаунт успешно создан!')
                return redirect('home_page')  
            else:
                messages.error(request, 'Не удалось зарегистрировать ваш аккаунт.')
    else:
        form = UserRegistrationForm()
    
    return render(request, 'polls/registration.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            identifier = form.cleaned_data['identifier']
            password = form.cleaned_data['password']
            user = authenticate(request, identifier=identifier, password=password)
            if user is not None:
                login(request, user)
                return redirect('home_page')
            else:
                form.add_error(None, 'Неверный телефон, email или пароль.')
    else:
        form = LoginForm()
    
    return render(request, 'polls/login.html', {'form': form})
