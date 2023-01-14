from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from profiles.forms import EditProfileForm


@login_required
def account(request):
    """
    input: request trên trang xem tài khoản (yêu cầu truy cập/thay đổi thông tin tài khoản)
    output:
        - xác thực và cập nhật thông tin tài khoản nếu có yêu cầu
        - trả về template html và context để render giao diện
    """
    # Nếu user điền form thay đổi thông tin tài khoản
    if request.method == "POST" and 'account-change-submit' in request.POST:
        password_form = PasswordChangeForm(request.user)
        user_form = EditProfileForm(request.POST, instance=request.user, user=request.user)
        if user_form.is_valid():
            user_form.save()
        else:
            # Nếu form không hợp lệ, lấy lại thông tin của user để thực hiện các bước xử lý tiếp theo
            user = User.objects.get(pk=request.user.id)
            request.user = user

    # Nếu user điền form thay đổi mật khẩu
    elif request.method == "POST" and 'password-change-submit' in request.POST:
        user_form = EditProfileForm(instance=request.user, user=request.user)
        password_form = PasswordChangeForm(request.user, request.POST)
        if password_form.is_valid():
            password_form.save()
            update_session_auth_hash(request, password_form.user)
    else:
        user_form = EditProfileForm(instance=request.user, user=request.user)
        password_form = PasswordChangeForm(request.user)

    context = {
        'password_form': password_form,
        'user_form': user_form,
    }
    
    return render(request, 'account.html', context)
