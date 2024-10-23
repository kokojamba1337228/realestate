from django.urls import path, include
from . import views

urlpatterns = [
    path('register/', views.user_register, name='register'),
    path('log-in/', views.user_login, name='login'),
    path('log-out/', views.user_logout, name='logout'), 

    # path('change_profile/', name='change_profile'),
]