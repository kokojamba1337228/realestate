from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from django.contrib.auth import get_user_model
from .forms import *
from polls.backends import EmailOrPhoneBackend
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from properties.models import Property 

User = get_user_model()

@login_required
def delete_favorite(request, property_id):
    if request.method == "DELETE":
        property_instance = get_object_or_404(Property, id=property_id)
        request.user.favorites.remove(property_instance)
        return JsonResponse({'status': 'deleted'})
    return JsonResponse({'error': 'Invalid request method'}, status=400)

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

def user_login(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            identifier = form.cleaned_data['identifier']
            password = form.cleaned_data['login_password']
            
            user = EmailOrPhoneBackend().authenticate(request, identifier=identifier, password=password)
            
            if user is not None:
                print(user.first_name)
                login(request, user)
                messages.success(request, f'Вы успешно вошли в аккаунт!')

                return redirect('home_page')    
            else:
                form.add_error(None, 'Неверный телефон, email или пароль.')
    else:
        form = LoginForm()
    
    return render(request, 'polls/login.html', {'form': form})

def user_logout(request):
    logout(request) 
    return redirect('login')

@login_required
def profile_view(request):
    user = request.user
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            return redirect('profile')  # Redirect to profile page after saving
    else:
        form = UserProfileForm(instance=user)
    
    # Fetch the user's favorite properties
    favorite_properties = user.favorites.all()

    return render(request, 'polls/profile.html', {
        'form': form,
        'favorite_properties': favorite_properties
    })
