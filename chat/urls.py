from django.urls import path
from . import views

urlpatterns = [
    path('', views.chat_list, name='chat_list'),
    path('create/<int:property_id>/', views.create_chat, name='create_chat'),
    path('<int:chat_id>/', views.chat_detail, name='chat_detail'),
    path('delete/<int:chat_id>/', views.delete_chat, name='delete_chat')]
