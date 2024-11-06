from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from django.contrib.auth import get_user_model
from .forms import *
from polls.backends import EmailOrPhoneBackend
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from properties.models import Property 
import json

User = get_user_model()

@login_required
@csrf_exempt
def delete_property(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        property_id = data.get('property_id')

        try:
            property = Property.objects.get(id=property_id, owner=request.user)
            property.delete()
            return JsonResponse({'status': 'deleted'})
        except Property.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Property not found'})

@login_required
@csrf_exempt
def delete_favorite(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        property_id = data.get('property_id')

        try:
            property = Property.objects.get(id=property_id)
            user = request.user
            user.favorites.remove(property)
            return JsonResponse({'status': 'removed'})
        except Property.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Property not found'})
        
        
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
    form = UserProfileForm(instance=user)

    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            return redirect('profile')

    favorite_properties = user.favorites.all()
    user_properties = Property.objects.filter(owner=user)

    return render(request, 'polls/profile.html', {
        'form': form,
        'favorite_properties': favorite_properties,
        'user_properties': user_properties
    })
