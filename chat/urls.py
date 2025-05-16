from django.urls import path
from .views import *

urlpatterns = [
    path('', chat_list, name='chat_list'),
    path('create/<int:property_id>/', create_chat, name='create_chat'),
    path('<int:chat_id>/', chat_detail, name='chat_detail'),
    path('delete/<int:chat_id>/', delete_chat, name='delete_chat'),
    path('send/', send_support_message, name='send_support_message'),
    path('get/', get_support_messages, name='get_support_messages'),
    path('admin/dashboard/', admin_dashboard, name='admin_dashboard'),
    path('admin/chat/<int:chat_id>/', admin_chat_detail, name='admin_chat_detail'),]
