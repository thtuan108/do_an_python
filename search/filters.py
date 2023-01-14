from profiles.models import Profile
import django_filters
from django import forms
from django_filters.filters import MultipleChoiceFilter


class ProfileFilter(django_filters.FilterSet):
    """
        Class lấy thông tin của đối tượng filter và hiển thị trên màn hình search
    """
    gender = MultipleChoiceFilter(label='', choices=Profile.GENDER, widget=forms.SelectMultiple(attrs={'title': 'Giới tính ▾'}))
    education = MultipleChoiceFilter(label='', choices=Profile.EDUCATION, widget=forms.SelectMultiple(attrs={'title': 'Học vấn ▾'}))
    relationship_status = MultipleChoiceFilter(label='', choices=Profile.RELATIONSHIP_STATUS, widget=forms.SelectMultiple(attrs={'title': 'Tình trạng quan hệ ▾'}))

    class Meta:
        model = Profile
        # add age
        fields = ['gender', 'education', 'relationship_status']
