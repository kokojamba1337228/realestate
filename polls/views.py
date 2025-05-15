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
from django.db import IntegrityError
from .models import *
from django.core.mail import send_mail
import random
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.timezone import now
from django.conf import settings
from django.contrib.auth.hashers import make_password

User = get_user_model()

token_generator = PasswordResetTokenGenerator()


def send_2fa_email(user):
    code = str(random.randint(100000, 999999))
    TwoFactorAuth.objects.update_or_create(user=user, defaults={"code": code, "created_at": now()})
    send_mail(
        'Your 2FA Code',
        f'Your verification code is {code}',
        'no-reply@example.com',
        [user.email],
    )

@login_required
def initiate_2fa(request):
    send_2fa_email(request.user)
    return render(request, "polls/2fa_verification.html")


def password_reset_code_view(request):
    if request.method == "POST":
        reset_code = request.POST.get("reset_code")
        new_password = request.POST.get("new_password")

        try:
            two_factor_auth = TwoFactorAuth.objects.get(code=reset_code)
            
            if two_factor_auth.is_expired():
                return render(request, "polls/password_reset_code.html", {"error": "Код истёк. Пожалуйста, запросите новый."})

            user = two_factor_auth.user
            user.password = make_password(new_password)
            user.save()

            two_factor_auth.delete()

            return redirect("login")
        except TwoFactorAuth.DoesNotExist:
            return render(request, "polls/password_reset_code.html", {"error": "Неверный код."})
    return render(request, "polls/password_reset_code.html")

def password_reset_request_view(request):
    if request.method == "POST":
        email = request.POST.get("email")
        try:
            user = CustomUser.objects.get(email=email)
            reset_code = str(random.randint(100000, 999999))
            
            TwoFactorAuth.objects.update_or_create(
                user=user,
                defaults={"code": reset_code, "created_at": timezone.now()},
            )

            send_mail(
                'Код для восстановления пароля',
                f'Ваш код для восстановления пароля: {reset_code}',
                settings.DEFAULT_FROM_EMAIL,
                [email],
            )
            return render(request, "polls/password_reset_request.html", {"success": "Код отправлен на вашу почту."})
        except CustomUser.DoesNotExist:
            return render(request, "polls/password_reset_request.html", {"error": "Пользователь с таким Email не найден."})
    return render(request, "polls/password_reset_request.html")

@login_required
def verify_2fa(request):
    if request.method == "POST":
        code = request.POST.get("code")
        try:
            auth = TwoFactorAuth.objects.get(user=request.user, code=code)
            if not auth.is_expired():
                return redirect("profile") 
            else:
                return render(request, "polls/2fa_verification.html", {"error": "Code expired"})
        except TwoFactorAuth.DoesNotExist:
            return render(request, "polls/2fa_verification.html", {"error": "Invalid code"})
    return render(request, "polls/2fa_verification.html")

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
    if request.method == "POST":
        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name")
        phone_number = request.POST.get("phone_number")
        email = request.POST.get("email")
        password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")

        if password != confirm_password:
            messages.error(request, "Пароли не совпадают")
            return render(request, "polls/registration.html", {
                "first_name": first_name,
                "last_name": last_name,
                "phone_number": phone_number,
                "email": email,
                "password": password,
                "confirm_password": confirm_password,
            })

        if User.objects.filter(email=email).exists():
            messages.error(request, "Электронная почта уже используется")
            return render(request, "polls/registration.html", {
                "first_name": first_name,
                "last_name": last_name,
                "phone_number": phone_number,
                "email": email,
                "password": password,
                "confirm_password": confirm_password,
            })
        if User.objects.filter(phone_number=phone_number).exists():
            messages.error(request, "Номер телефона уже используется")
            return render(request, "polls/registration.html", {
                "first_name": first_name,
                "last_name": last_name,
                "phone_number": phone_number,
                "email": email,
                "password": password,
                "confirm_password": confirm_password,
            })

        try:
            user = User.objects.create_user(
                first_name=first_name,
                last_name=last_name,
                phone_number=phone_number,
                email=email,
                password=password,
            )
            user.save()
            login(request, user)
            return redirect("home_page")
        except IntegrityError:
            messages.error(request, "Ошибка при регистрации. Попробуйте снова.")
            return render(request, "polls/registration.html", {
                "first_name": first_name,
                "last_name": last_name,
                "phone_number": phone_number,
                "email": email,
                "password": password,
                "confirm_password": confirm_password,
            })

    return render(request, "polls/registration.html")

def user_login(request):
    unauth_add_property = request.GET.get('unauth_add_property', 'false') == 'true'
    unauth_account = request.GET.get('unauth_account', 'false') == 'true'
    unauth_chat = request.GET.get('unauth_chat', 'false') == 'true'
    unauth_favorite = request.GET.get('unauth_favorite', 'false') == 'true'

    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            identifier = form.cleaned_data['identifier']
            password = form.cleaned_data['login_password']

            user = EmailOrPhoneBackend().authenticate(request, identifier=identifier, password=password)

            if user is not None:
                login(request, user)
                messages.success(request, 'Вы успешно вошли в аккаунт!')
                return redirect(request.GET.get('next', 'home_page'))
            else:
                messages.error(request, 'Неверный телефон, email или пароль.')
    else:
        form = LoginForm()
        if unauth_add_property:
            messages.warning(request, 'Пожалуйста, войдите в аккаунт, чтобы добавить объявление.')
        if unauth_account:
            messages.warning(request, 'Пожалуйста, войдите в аккаунт, чтобы просмотреть профиль.')
        if unauth_chat:
            messages.warning(request, 'Пожалуйста, войдите в аккаунт, чтобы использовать чаты.')
        if unauth_favorite:
            messages.warning(request, 'Пожалуйста, войдите в аккаунт, чтобы добавить в избранное.')

    return render(request, 'polls/login.html', {'form': form})

def user_logout(request):
    logout(request) 
    return redirect('main')

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
