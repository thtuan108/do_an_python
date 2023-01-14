from django.shortcuts import redirect, reverse
from django.http import JsonResponse


def premium_required(function):
    """
    Điều hướng qua trang subscribe cho những tính năng cần tài khoản premium
    TODO: Phát triển thêm tính năng tài khoản premium để xử lý logic này
    """
    def wrap(request, *args, **kwargs):
        if request.is_ajax():
            data = {}
            data['redirect'] = '/subscribe'
            return JsonResponse(data)
        return redirect(reverse('subscribe'))

    return wrap
