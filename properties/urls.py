from django.urls import path
from .views import *

urlpatterns = [
    path('home/', property_home, name='home_page'),
    path('add/', add_property, name='add_property'),
    path('detail/<int:id>/', property_detail, name='property_detail'),
    path('remove-favorite/<int:property_id>/', remove_favorite, name='remove_favorite'),] 
