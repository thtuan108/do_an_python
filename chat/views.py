from django.shortcuts import render, reverse, redirect
from .forms import MessageForm
from .models import Conversations, Messages, Winks, Views, Reject
from django.contrib.auth.models import User
from django.http import JsonResponse, HttpResponse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q
from django.contrib import messages
from checkout.decorators import premium_required
from django.contrib.auth.decorators import login_required


@login_required
def new_message_check(request):
    """
    input: thông tin cuộc hội thoại của user
    output: true nếu user đã đọc, false nếu user chưa đọc
    """
    conversation_id = request.GET.get('url_id', None)
    is_read = Messages.objects.filter(conversation=conversation_id, receiver=request.user, is_read=False).exists()
    data = {
        'conversation': is_read
    }
    return JsonResponse(data)


def read_messages(request):
    """
    input: tin nhắn của user
    output: đánh dấu tin nhắn này là đã đọc
    """
    conversation_id = request.GET.get('url_id', None)
    messages = Messages.objects.filter(conversation=conversation_id)
    for message in messages:
        if message.receiver == request.user:
            message.is_read = True
            message.save()

    is_read = Messages.objects.filter(conversation=conversation_id, receiver=request.user, is_read=False).exists()
    data = {
        'conversation': is_read
    }
    return JsonResponse(data)


@login_required
def chat(request, id):
    """
    input: thông tin user và id của cuộc hội thoại
    output: file chat.html và context chứa mapping để render giao diện chat
    """
    page_ref = "chat"
    conversation_ids = Conversations.objects.filter(participants=request.user)
    
    all_conversations = {}
    is_read_check = {}
    for conversation in conversation_ids:  
        all_conversations[conversation.id] = Messages.objects.filter(conversation=conversation).last()

        # Kiểm tra trạng thái hội thoại là đã xem/chưa xem để đánh dấu thể hiện trên giao diện
        last_message = Messages.objects.filter(conversation=conversation, receiver=request.user).last()
        if last_message:
            is_read_check[conversation.id] = last_message.is_read
        else: 
            is_read_check[conversation.id] = True
    
    messages = Messages.objects.filter(conversation=id)
    
    # Lấy thông tin người nhận
    conversation = Conversations.objects.get(pk=id)
    participants = conversation.participants.all()
    for user in participants:
        if not user.id == request.user.id:
            receiver = user
    
    # Nếu có tin nhắn được yêu cầu gửi
    if request.method == "POST":
        message_form = MessageForm(request.POST)
        if message_form.is_valid():
            # Nếu user tự gửi tin nhắn cho chính mình
            if receiver.id == request.user.id:
                messages.success(request, "Bạn không thể gửi tin nhắn cho chính mình")
                return redirect(reverse('chat_home'))
                
            # Lưu lại tin nhắn
            message = message_form.save(commit=False)
            message.receiver = User.objects.get(id=receiver.id)
            message.sender = request.user
            message.conversation = conversation
            message.save()

        context = {
            'page_ref': page_ref,
            'user_messages': messages,
            'message_form':message_form,
            'all_conversations': all_conversations,
            'receiver': receiver,
            'conversation_id': int(id),
            'is_read_check': is_read_check
        }
        
        return redirect(reverse('chat', kwargs={'id':id}))
    else:
        message_form = MessageForm()
    
    context = {
        'page_ref': page_ref,
        'user_messages': messages,
        'message_form':message_form,
        'all_conversations': all_conversations,
        'receiver': receiver.id,
        'conversation_id': int(id),
        'is_read_check': is_read_check
    }
    
    return render(request, 'chat.html', context)
 

@login_required  
def chat_home(request):
    """
    input: request của user yêu cầu truy cập trang tin nhắn
    output: file chat_home.html và các context để render giao diện, hiển thị danh sách tin nhắn
    """
    conversation_ids = Conversations.objects.filter(participants=request.user)

    all_conversations = {}
    is_read_check = {}
    for conversation in conversation_ids:  
        all_conversations[conversation.id] = Messages.objects.filter(conversation=conversation).last()
        
        # Đánh dấu nếu tin nhắn đã được đọc
        last_message = Messages.objects.filter(conversation=conversation, receiver=request.user).last()
        if last_message:
            is_read_check[conversation.id] = last_message.is_read
        else: 
            is_read_check[conversation.id] = True

    context = {
        'user_messages': messages,
        'all_conversations': all_conversations,
        'conversation_id': None,
        'is_read_check': is_read_check
    }

    return render(request, 'chat_home.html', context)


def wink(request):
    """
    input: request gửi lượt thích đến một user
    output: lưu lại lượt thích đã được gửi đi
    """
    
    # Lấy id của user nhận
    receiver_id = request.GET.get('receiver_id')
    # Nếu user tự gửi lượt thích cho chính mình
    if receiver_id == request.user.id:
        data = {}
        data['message'] = "Bạn không thể tự gửi lượt thích cho chính mình"
        return JsonResponse(data)
        
    # Nếu lượt thích gần đây nhất đã được xem, đánh dấu trạng thái thể hiện trên UI
    current_wink = Winks.objects.filter(Q(receiver_id=receiver_id) & Q(sender_id=request.user.id) & Q(is_read=False)).exists()
    if current_wink:
        data = {}
        data['message'] = "Lượt thích gần đây nhất của bạn chưa được xem"
        return JsonResponse(data)
    
    # Lưu lại lượt thích trong database
    wink = Winks(receiver=User.objects.get(pk=receiver_id), sender=request.user)
    data = {}
    try:
        wink.save()
    except:
        data['message'] = 'Có lỗi xảy ra'
    finally:
        data['message'] = 'Đã gửi lượt thích.'
    return JsonResponse(data)


@login_required
def chat_ajax(request):
    """
    input: nội dung tin nhắn và thông tin người gửi / nhận
    output: JSON object thông báo tin nhắn đã được gửi hoặc bị lỗi
    """
    # Lấy thông tin người nhận và nội dung tin nhắn
    receiver_id = request.POST.get('message_receiver')
    message_content = request.POST.get('message_content')
    
    # Nếu user tự gửi tin cho chính mình
    if receiver_id == request.user.id:
        data = {}
        data['message'] = "Bạn không thể gửi tin nhắn cho chính mình!"
        return JsonResponse(data)
    
    conversation = Conversations.objects.filter(participants=request.user.id).filter(participants=receiver_id)
    # Nếu đã có lịch sử trò chuyện, tạo và lưu tin nhắn mới
    if conversation.exists():
        try:
            message = Messages(
            receiver=User.objects.get(pk=receiver_id),
            sender=request.user,
            message_content=message_content,
            is_read=False,
            conversation=conversation[0]
            )
            message.save()
            data = {}
            data['message'] = "Tin nhắn đã gửi"
            return JsonResponse(data)
        except:
            data = {}
            data['message'] = "Có lỗi! Chưa gửi được tin nhắn!"
            return JsonResponse(data)
    # Nếu chưa có lịch sử trò chuyện, tạo cuộc hội thoại và tin nhắn mới
    else:
        try:
            # Tạo mới hội thoại
            conversation = Conversations()
            conversation.save()
            conversation.participants.add(request.user)
            conversation.participants.add(User.objects.get(pk=receiver_id))
            # Tạo tin nhắn mới
            message = Messages(
                receiver=User.objects.get(pk=receiver_id),
                sender=request.user,
                message_content=message_content,
                is_read=False,
                conversation=conversation
                )
            message.save()
            data = {}
            data['message'] = "Tin nhắn đã gửi"
            return JsonResponse(data)
        except:
            data = {}
            data['message'] = "Có lỗi! Chưa gửi được tin nhắn!"
            return JsonResponse(data)


@login_required
def winks(request):
    """
    input: yêu cầu xem lượt thích và phân trang
    output: file template và context để render giao diện
    """

    # Lấy thông tin lượt thích và phân trang hiển thị
    winks = Winks.objects.filter(receiver=request.user.id).order_by('-created_on')
    winks_paginated = Paginator(winks, 6)

    page = request.GET.get('page')
    try:
        winks_page = winks_paginated.page(page)
    except PageNotAnInteger:
        winks_page = winks_paginated.page(1)
        page = 1
    except EmptyPage:
        winks_page = winks_paginated.page(winks_paginated.num_pages)
        page = winks_paginated.num_pages

    context = {
        'page_ref': 'wink',
        'winks_page': winks_page,
        'page': page
    }

    return render(request, 'winks.html', context)


@login_required
def views(request):
    """
    input: yêu cầu xem lượt xem và phân trang
    output: file template và context để render giao diện
    """
    # Lấy thông tin lượt xem và phân trang hiển thị
    views = Views.objects.filter(receiver=request.user.id).order_by('-created_on')
    views_paginated = Paginator(views, 6)
    
    page = request.GET.get('page')
    try:
        views_page = views_paginated.page(page)
    except PageNotAnInteger:
        views_page = views_paginated.page(1)
        page = 1
    except EmptyPage:
        views_page = views_paginated.page(views_paginated.num_pages)
        page = views_paginated.num_pages
        
    context = {
        'page_ref': 'view',
        'views_page': views_page,
        'page': page
    }
    
    return render(request, 'views.html', context)


@login_required
@premium_required
def read_wink(request):
    """
    input: yêu cầu xem lượt thích tại một trang
    output: đánh dấu lượt thích là đã xem
    """
    page = request.GET.get('page', None)
    
    winks = Winks.objects.filter(receiver=request.user.id).order_by('-created_on')
    winks_paginated = Paginator(winks, 6)
    
    try:
        winks_page = winks_paginated.page(page)
    except PageNotAnInteger:
        winks_page = winks_paginated.page(1)
    except EmptyPage:
        winks_page = winks_paginated.page(winks_paginated.num_pages)
    
    for wink in winks_page:
        wink.is_read = True
        wink.save()
        
    return HttpResponse(status=204)


@login_required
@premium_required
def read_view(request):
    """
    input: yêu cầu xem lượt xem hồ sơ tại một trang
    output: đánh dấu lượt xem là đã xem
    """

    page = request.GET.get('page', None)
    
    views = Views.objects.filter(receiver=request.user.id).order_by('-created_on')
    views_paginated = Paginator(views, 6)
    
    try:
        views_page = views_paginated.page(page)
    except PageNotAnInteger:
        views_page = views_paginated.page(1)
    except EmptyPage:
        views_page = views_paginated.page(views_paginated.num_pages)
    
    for view in views_page:
        view.is_read = True
        view.save()
        
    return HttpResponse(status=204)
