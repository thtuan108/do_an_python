from django.shortcuts import render, reverse, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import OrderForm, MakePaymentForm
from .models import Subscription
from django.utils import timezone
from profiles.models import Profile


def make_user_premium(request):
    """
    input: thông tin user
    output: cập nhật thông tin tài khoản user thành premium
    """
    profile = Profile.objects.get(user_id=request.user.id)
    profile.is_premium = True
    profile.save()
    
    return


@login_required
def subscribe(request):
    """
    input: request vào màn hình subscribe (bao gồm thông tin trong form đăng ký premium)
    output: file subscribe.html và context chứa các mapping để render giao diện
    """
    plan_ids = {
        'plan_one_month': 'Tháng - 200.000đ',
        'plan_three_month': '3 Tháng - 300.000đ',
        'plan_six_month': '6 Tháng - 400.000đ'
    }

    # Nếu có thông tin trong form đăng ký premium
    if request.method == 'POST':
        order_form = OrderForm(request.POST)
        payment_form = MakePaymentForm(request.POST)
        if order_form.is_valid() and payment_form.is_valid():
            order = order_form.save(commit=False)
            order.date = timezone.now()
            order.save()

            subscription = Subscription.objects.filter(user_id=request.user.id).first()

            # Nếu user đã có đăng ký gói tài khoản trước đây thì thực hiện cập nhật
            if subscription:
                # Lưu lại lượt đăng ký mới
                subscription = Subscription(
                    user=request.user,
                    plan=plan_ids[order.plans],
                )
                subscription.save()
                make_user_premium(request)
                messages.error(request, "Thành công! Tài khoản đã được nâng cấp Premium")
                return redirect(reverse('index'))
            # Nếu user chưa đăng ký gói tài khoản trước đây thì tạo mới
            else:
                subscription = Subscription(
                    user=request.user,
                    plan=plan_ids[order.plans],
                )
                subscription.save()
                make_user_premium(request)
                messages.error(request, "Thành công! Tài khoản đã được nâng cấp Premium")
                return redirect(reverse('index'))
        else:
            messages.error(request, "Có lỗi xảy ra! Không thể cập nhật thông tin")
    # Nếu không có thông tin đăng ký trong form
    else:
        payment_form = MakePaymentForm()
        order_form = OrderForm()

    return render(request, 'subscribe.html', {'page_ref': 'subscribe', 'order_form': order_form, 'payment_form': payment_form})

