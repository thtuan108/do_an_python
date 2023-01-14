from django.shortcuts import render
from profiles.models import Profile
from django.db.models import Q
from django.contrib.auth.decorators import login_required
import datetime as DT


@login_required
def index(request):
    """
    input: request truy cập của user đã đăng nhập
    output: file home.html và các tham số như hồ sơ người dùng để render
    """

    # Danh sách những người dùng ở gần
    # TODO: Tính năng sẽ phát triển sau, tạm thời lấy ngẫu nhiên 4 hồ sơ
    if request.user.profile.looking_for == "BOTH":
        closest_profiles = Profile.objects.filter(Q(looking_for=request.user.profile.gender) | Q(looking_for="BOTH")).exclude(user_id=request.user.id).all()[:4]
    else:
        closest_profiles = Profile.objects.filter(Q(looking_for=request.user.profile.gender) | Q(looking_for="BOTH")).filter(gender=request.user.profile.looking_for).exclude(user_id=request.user.id).all()[:4]

    today = DT.date.today()
    one_week_ago = today - DT.timedelta(days=7)

    # Danh sách những người hoạt động gần đây
    # Lọc theo tiêu chí những người có đăng nhập trong vòng 7 ngày, trừ những người mới đăng ký trong 7 ngày
    if request.user.profile.looking_for == "BOTH":
        active_profiles = Profile.objects.filter(Q(looking_for=request.user.profile.gender) | Q(looking_for="BOTH")).filter(user__date_joined__lte=one_week_ago).order_by('-user__last_login').exclude(user_id=request.user.id).all()[:4]
    else:
        active_profiles = Profile.objects.filter(Q(looking_for=request.user.profile.gender) | Q(looking_for="BOTH")).filter(gender=request.user.profile.looking_for).filter(user__date_joined__lte=one_week_ago).order_by('-user__last_login').exclude(user_id=request.user.id).all()[:4]
    
    # Danh sách thành viên mới (đăng ký trong vòng 7 ngày)
    if request.user.profile.looking_for == "BOTH":
        newest_profiles = Profile.objects.filter(Q(looking_for=request.user.profile.gender) | Q(looking_for="BOTH")).order_by('-user__date_joined').exclude(user_id=request.user.id).all()[:4]
    else:
        newest_profiles = Profile.objects.filter(Q(looking_for=request.user.profile.gender) | Q(looking_for="BOTH")).filter(gender=request.user.profile.looking_for).order_by('-user__date_joined').exclude(user_id=request.user.id).all()[:4]

    context = {
        'page_ref': 'home',
        'closest_profiles': closest_profiles,
        'active_profiles': active_profiles,
        'newest_profiles': newest_profiles,
    }
    
    return render(request, 'home.html', context)


def preregister(request):
    """
    input: request của user chưa đăng nhập
    output: trang index.html chứa các thông tin cơ bản
    """

    return render(request, 'index.html')
