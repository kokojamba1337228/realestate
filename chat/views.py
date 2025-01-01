from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, HttpResponseNotAllowed
from .models import Chat, Message
from properties.models import Property
from django.contrib.auth.decorators import login_required

@login_required
def chat_list(request):
    chats = Chat.objects.filter(participants=request.user)
    chat_data = []

    for chat in chats:
        other_user = chat.participants.exclude(id=request.user.id).first()
        last_message = chat.messages.last()
        chat_data.append({
            'chat': chat,
            'other_user': other_user,
            'last_message': last_message.content if last_message else "",
            'avatar': other_user.avatar.url if other_user.avatar else None,
            'initial': other_user.first_name[0] if other_user.first_name else "U",
        })

    return render(request, 'chat/chat_list.html', {'chats': chat_data})

@login_required
def chat_detail(request, chat_id):
    chat = get_object_or_404(Chat, id=chat_id)
    other = chat.participants.exclude(id=request.user.id).first()

    if request.user not in chat.participants.all():
        return HttpResponse("You are not a participant in this chat.", status=403)
    
    messages = chat.messages.all()
    
    if request.method == 'POST':
        message_content = request.POST.get('message')
        if message_content:
            Message.objects.create(chat=chat, sender=request.user, content=message_content)
            return redirect('chat_detail', chat_id=chat.id)
    
    return render(request, 'chat/chat_detail.html', {'chat': chat, 'messages': messages, 'other': other})

@login_required
def create_chat(request, property_id):
    property = get_object_or_404(Property, id=property_id)
    
    chat = Chat.objects.create(property=property)
    chat.participants.add(request.user, property.owner)
    
    return redirect('chat_detail', chat_id=chat.id)

@login_required
def delete_chat(request, chat_id):
    if request.method == "POST":
        chat = get_object_or_404(Chat, id=chat_id)
        if chat.participants.filter(id=request.user.id).exists():
            chat.delete()
        return redirect('chat_list')
    return HttpResponseNotAllowed(['POST'])