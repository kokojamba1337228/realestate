from django.urls import path, include
from .views import *
from django.contrib.auth.views import LogoutView

urlpatterns = [
    path('register/', user_register, name='register'),
    path('log-in/', user_login, name='login'),
    path('log-out/', LogoutView.as_view(next_page='home_page'), name='logout'), 
    path('profile/', profile_view, name='profile'),
    path('user/account/delete_favorite/<int:property_id>/', delete_favorite, name='delete_favorite_account'),]
    #path('<int:user_id>/', views.user_profile, name='profile'),