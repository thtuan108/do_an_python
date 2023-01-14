from django.shortcuts import render, redirect, reverse
from django.contrib import auth
from django.forms import modelformset_factory
from profiles.forms import UserLoginForm, UserRegistrationForm, ProfileForm, ProfileImageForm, MessagesForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .models import ProfileImage
from chat.models import Conversations, Views
from checkout.models import Subscription


def height_choices(member_height):
    """
    input: thông tin chiều cao bằng số nhập từ form
    output: chuỗi hiển thị chiều cao có thêm đơn vị cm để hiển thị trên UI
    """
    height = {
        '150.00': '150 cm',
        '155.00': '155 cm',
        '160.00': '160 cm',
        '165.00': '165 cm',
        '170.00': '170 cm',
        '175.00': '175 cm',
        '180.00': '180 cm',
        '185.00': '185 cm',
        '190.00': '190 cm',
        }
        
    return height[member_height]


@login_required
def logout(request):
    """
    input: request yêu cầu đăng xuất
    output: logout cho user và trả về url điều hướng về trang giới thiệu
    """
    auth.logout(request)
    messages.success(request, "Bạn đã đăng xuất")
    return redirect(reverse('preregister'))


@login_required
def delete(request):
    """
    input: request yêu cầu xóa tài khoản
    output: xóa tài khoản user và trả về url điều hướng về trang giới thiệu
    """
    try:
        user = User.objects.get(pk=request.user.id)
        user.delete()
        messages.success(request, "Tài khoản của bạn đã được xóa")
    except:
        messages.success(request, "Có lỗi xảy ra!")
        
    return redirect(reverse('preregister'))


def login(request):
    """
    input: request yêu cầu đăng nhập
    output:
        - Nếu user có gửi thông tin đăng nhập trong form: login user và điều hướng đến trang chủ
        - Nếu chưa điền thông tin đăng nhập: hiển thị form đăng nhập trống
    """
    # Nếu user đã đăng nhập, đưa thẳng về trang chủ
    if request.user.is_authenticated:
        return redirect(reverse('index'))
        
    # Nếu user điền thông tin đăng nhập
    if request.method == "POST":
        login_form = UserLoginForm(request.POST)
        if login_form.is_valid():
            user = auth.authenticate(username=request.POST['username'], password=request.POST['password'])
            if user:
                messages.success(request, "Đăng nhập thành công")
                auth.login(user=user, request=request)
                return redirect(reverse('index'))
            else: 
                messages.error(request, "Tên hoặc mật khẩu không chính xác")
    else:
        login_form = UserLoginForm()
            
    context = {
        'login_form': login_form
    }
    return render(request, 'login.html', context)
    

def register(request):
    """
        input: request yêu cầu đăng ký tài khoản
        output:
            - Nếu user có gửi thông tin đăng ký trong form: login user và điều hướng đến tạo hồ sơ
            - Nếu chưa điền thông tin đăng nhập: hiển thị form đăng ký để điền vào
        """
    # Nếu user gửi thông tin đăng ký trong form
    if request.method == "POST":
        registration_form = UserRegistrationForm(request.POST)

        if registration_form.is_valid():
            registration_form.save()
            
            user = auth.authenticate(username=request.POST['username'], password=request.POST['password1'])
            
            if user:
                messages.success(request, "Tạo tài khoản thành công")
                auth.login(user=user, request=request)
                return redirect(reverse('create_profile'))
            else:
                messages.error(request, "Có lỗi xảy ra. Không thể tạo tài khoản.")
    else:
        registration_form = UserRegistrationForm()

    context = {
        'registration_form': registration_form
    }
    return render(request, 'register.html', context)


@login_required
def create_profile(request):
    """
    input: request tạo / cập nhật hồ sơ
    output:
        - nếu user điền thông tin cập nhật trong form: thực hiện cập nhật và chuyển qua trang thông báo xác nhận
        - nếu không có thông tin cập nhật trong form: trả về form trống cho user thao tác
    """

    # Form upload nhiều ảnh cùng lúc
    ImageFormSet = modelformset_factory(ProfileImage, form=ProfileImageForm, extra=6, max_num=6, help_texts=None)
    
    # Nếu user có điền thông tin cập nhật
    if request.method == "POST":
        profile_form = ProfileForm(request.POST, instance=request.user.profile)
        image_form = ProfileImageForm(request.POST, request.FILES)
        
        formset = ImageFormSet(request.POST, request.FILES,
                              queryset=ProfileImage.objects.filter(user_id=request.user.id).all())

        if profile_form.is_valid() and formset.is_valid():
            # Cập nhật các thông tin vào database
            instance = profile_form.save(commit=False)
            instance.user_id = request.user.id
            instance.save()

            # Xóa các ảnh được yêu cầu
            deleted_images = request.POST.getlist('delete')
            for image in deleted_images:
                if not image == "None":
                    ProfileImage.objects.get(pk=image).delete()

            # Lưu các ảnh được upload
            for form in formset:
                if form.is_valid() and form.has_changed():
                    instance_image = form.save(commit=False)
                    instance_image.user = request.user
                    instance_image.save()

            return redirect(reverse('verification_message'))
            
    else:
        profile_form = ProfileForm(instance=request.user.profile)
        image_form = ProfileImageForm(instance=request.user.profile)
        initial_images = [{'image_url': i.image} for i in ProfileImage.objects.filter(user_id=request.user.id).all() if i.image]
        formset = ImageFormSet(queryset=ProfileImage.objects.filter(user_id=request.user.id).all(), initial=initial_images)
        
    context = {
        'page_ref': 'create_profile',
        'profile_form': profile_form,
        'image_form': image_form,
        'formset': formset
    }
        
    return render(request, 'create-profile.html', context)    


@login_required
def member_profile(request, id):
    """
    input: request xem thông tin hồ sơ người dùng, id của người dùng
    output: trả về trang member.html và mapping hiển thị chi tiết thông tin hồ sơ người dùng
    """
    member = User.objects.get(id=id)
    height = height_choices(str(member.profile.height))

    # Nếu hồ sơ này không phải của user gửi request
    if not member == request.user:
        current_user = False
        
        # Lưu thông tin lượt xem
        last_view = Views.objects.filter(receiver_id=id).filter(sender_id=request.user.id).last()
        if not last_view or last_view.is_read:
            view = Views(receiver=member, sender=request.user)
            view.save()
        
        # Nếu user gửi tin nhắn
        if request.method == "POST" and 'message_submit' in request.POST:
            message_form = MessagesForm(request.POST)
            if message_form.is_valid():
                # Nếu user có tài khoản premium
                if request.user.profile.is_premium:
                    # Tạo cuộc trò chuyện mới (nếu chưa có) và bắt đầu nhắn tin
                    conversation = Conversations.objects.filter(participants=request.user.id).filter(participants=id)
                    if conversation.exists():
                        message = message_form.save(commit=False)
                        message.sender = request.user
                        message.receiver = User.objects.get(pk=id)
                        message.conversation = conversation[0]
                        message.save()
                        return redirect('/chat/%s' % conversation[0].id )
                    else:
                        receiver = User.objects.get(pk=id)
                        conversation = Conversations()
                        conversation.save()
                        conversation.participants.add(request.user.id)
                        conversation.participants.add(receiver)
                        message = message_form.save(commit=False)
                        message.sender = request.user
                        message.receiver = receiver
                        message.conversation = conversation
                        message.save()
                        return redirect('/chat/%s' % conversation.id )
                #  Nếu user chưa có premium
                else:
                    return redirect(reverse('subscribe'))
        else:
            message_form = MessagesForm()
    else:
        message_form = MessagesForm()
        current_user = True
        
    context = {
        'height': height,
        'page_ref': 'member_profile',
        'member': member,
        'message_form': message_form,
        'current_user': current_user
    }
    return render(request, 'member.html', context)


def verification_message(request):
    """
    Render trang thông báo xác nhận
    """
    return render(request, 'verification-message.html')