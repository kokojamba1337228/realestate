from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.user_register, name='register'),
    path('log-in/', views.login_view, name='login'),
    # path('log-out/', name='profile'),
    # path('change_profile/', name='change_profile'),
]