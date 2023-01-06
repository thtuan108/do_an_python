from .models import Subscription
import stripe
from django.shortcuts import render, redirect, reverse
from django.http import JsonResponse
from django.contrib.auth.models import User
from profiles.models import Profile


def premium_required(function):
    def wrap(request, *args, **kwargs):
        if request.is_ajax():
            data = {}
            data['redirect'] = '/subscribe'
            return JsonResponse(data)
        return redirect(reverse('subscribe'))
            
    return wrap
