from django.urls import path
from . import views

urlpatterns = [
    path('home/', views.property_list, name='home_page'),
] 
