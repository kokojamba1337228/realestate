from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, HttpResponseNotAllowed, JsonResponse
from .models import Chat, Message, SupportChat, SupportMessage
from properties.models import Property
from polls.models import CustomUser
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
import json
from django.db.models import Q


@login_required
def chat_list(request):
    chats = Chat.objects.filter(Q(buyer=request.user) | Q(seller=request.user))
    chat_data = []

    for chat in chats:
        other_user = chat.buyer if request.user == chat.seller else chat.seller
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

    if request.user != chat.buyer and request.user != chat.seller:
        return HttpResponse("You are not authorized to access this chat.", status=403)

    messages = chat.messages.all()
    other_user = chat.buyer if request.user == chat.seller else chat.seller

    if request.method == 'POST':
        message_content = request.POST.get('message')
        if message_content:
            message = Message.objects.create(chat=chat, sender=request.user, content=message_content)
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({
                    'sender': message.sender.first_name,
                    'content': message.content,
                    'created_at': message.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                })

    return render(request, 'chat/chat_detail.html', {
        'chat': chat,
        'messages': messages,
        'other_user': other_user
    })


@login_required
def create_chat(request, property_id):
    property = get_object_or_404(Property, id=property_id)

    if request.user == property.owner:
        return HttpResponse("You cannot start a chat with yourself.", status=403)

    existing_chat = Chat.objects.filter(buyer=request.user, seller=property.owner, property=property).first()

    if existing_chat:
        return redirect('chat_detail', chat_id=existing_chat.id)

    chat = Chat.objects.create(buyer=request.user, seller=property.owner, property=property)

    return redirect('chat_detail', chat_id=chat.id)

@login_required
def delete_chat(request, chat_id):
    if request.method == "POST":
        chat = get_object_or_404(Chat, id=chat_id)
        chat.delete()
        return redirect('chat_list')
    return HttpResponseNotAllowed(['POST'])

@login_required
@csrf_exempt
def send_support_message(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        content = data.get('content')

        admin = CustomUser.objects.filter(is_superuser=True).first()
        chat, created = SupportChat.objects.get_or_create(user=request.user, admin=admin)

        message = SupportMessage.objects.create(chat=chat, sender=request.user, content=content)
        return JsonResponse({'status': 'ok', 'message': message.content})
    return JsonResponse({'status': 'error'}, status=400)

@login_required
def get_support_messages(request):
    admin = CustomUser.objects.filter(is_superuser=True).first()
    chat = SupportChat.objects.filter(user=request.user, admin=admin).first()

    if not chat:
        return JsonResponse({'messages': []})

    messages = chat.messages.select_related('sender').all()
    message_data = []
    for msg in messages:
        message_data.append({
            'sender__first_name': msg.sender.first_name,
            'sender__id': msg.sender.id,
            'content': msg.content,
            'timestamp': msg.timestamp.isoformat(),
            'sender_avatar': msg.sender.avatar.url if msg.sender.avatar else ''
        })

    return JsonResponse({'messages': message_data})

from django.contrib.admin.views.decorators import staff_member_required

@staff_member_required
def admin_support_dashboard(request):
    chats = SupportChat.objects.select_related('user').all()
    return render(request, 'chat/admin_dashboard.html', {'chats': chats})

@staff_member_required
@csrf_exempt
def admin_send_message(request, chat_id):
    if request.method == 'POST':
        data = json.loads(request.body)
        content = data.get('content')
        chat = get_object_or_404(SupportChat, id=chat_id)
        SupportMessage.objects.create(chat=chat, sender=request.user, content=content)
        return JsonResponse({'status': 'ok'})
    return JsonResponse({'status': 'error'}, status=400)

@staff_member_required
def get_chat_messages(request, chat_id):
    chat = get_object_or_404(SupportChat, id=chat_id)
    messages = chat.messages.all().values('sender__first_name', 'sender__id', 'content', 'timestamp')
    return JsonResponse({'messages': list(messages)})
