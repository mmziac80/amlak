# -*- coding: utf-8 -*-
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import ChatRoom, Message
from .forms import MessageForm

@login_required
def chat_room(request, room_id):
    """نمایش اتاق چت"""
    room = get_object_or_404(ChatRoom, id=room_id, users=request.user)
    messages = room.messages.all()
    form = MessageForm()
    
    if request.method == 'POST':
        form = MessageForm(request.POST, request.FILES)
        if form.is_valid():
            message = form.save(commit=False)
            message.room = room
            message.sender = request.user
            message.save()
            return redirect('chat:room', room_id=room.id)
            
    return render(request, 'chat/room.html', {
        'room': room,
        'messages': messages,
        'form': form
    })

@login_required 
def send_message(request, room_id):
    """ارسال پیام با AJAX"""
    if request.method == 'POST':
        room = get_object_or_404(ChatRoom, id=room_id, users=request.user)
        content = request.POST.get('content')
        
        message = Message.objects.create(
            room=room,
            sender=request.user,
            content=content
        )
        
        return JsonResponse({
            'status': 'success',
            'message': {
                'id': message.id,
                'content': message.content,
                'sender': message.sender.get_full_name(),
                'created_at': message.created_at.strftime('%H:%M')
            }
        })
    return JsonResponse({'status': 'error'}, status=400)
