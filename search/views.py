from django.shortcuts import render
from profiles.models import Profile
from .filters import ProfileFilter
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

@login_required
def search(request):
    """
    input:
        request có payload gồm thông tin chiều cao, giới tính, tình trạng quan hệ
    output:
        file html và context lưu các kết quả tìm kiếm để render giao diện
    """
    
    # Lấy thông tin lọc tìm kiếm
    min_height = request.GET.get('height_min', '0')
    max_height = request.GET.get('height_max', '200')
    user_gender = "NAM" if request.user.profile.gender == "NAM" else "NỮ"

    # Tạo bộ lọc tìm kiếm
    qs = Profile.objects.filter(Q(looking_for=user_gender) | Q(looking_for="BOTH")).exclude(user_id=request.user.id)

    # Thêm thông tin chiều cao vào bộ lọc
    if min_height: 
        qs = qs.filter(height__gte=min_height)
    if max_height:
        qs = qs.filter(height__lte=max_height)

    # Lấy kết quả theo bộ lọc
    filtered_result = ProfileFilter(request.GET, queryset=qs)
    
    # Phân trang
    search_paginated = Paginator(filtered_result.qs, 12)

    page = request.GET.get('page')
    try:
        search_page = search_paginated.page(page)
    except PageNotAnInteger:
        search_page = search_paginated.page(1)
        page = 1
    except EmptyPage:
        search_page = search_paginated.page(search_paginated.num_pages)
        page = search_paginated.num_pages
    
    context = {
        'page_ref': 'search',
        'filtered_result': filtered_result,
        'page': page,
        'search_page': search_page,
        'min_height': min_height,
        'max_height': max_height,
    }
    
    return render(request, 'search.html', context)

