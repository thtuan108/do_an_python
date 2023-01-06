from profiles.models import Profile
import django_filters
from django import forms
from django_filters.filters import MultipleChoiceFilter, RangeFilter, NumericRangeFilter
from django_filters.widgets import RangeWidget
# Filter for bisexual users
class ProfileFilter(django_filters.FilterSet):
    relationship_status = MultipleChoiceFilter(label='', choices=Profile.RELATIONSHIP_STATUS, widget=forms.SelectMultiple(attrs={'title': 'Tình trạng quan hệ ▾'}))
    gender = MultipleChoiceFilter(label='', choices=Profile.GENDER, widget=forms.SelectMultiple(attrs={'title': 'Giới tính ▾'}))

    
    class Meta:
        model = Profile
        # add age
        fields = ['relationship_status', 'gender']
        labels = {'relationship_status': 'Tình trạng quan hệ', 'education': 'Học vấn'}

# Filter not for bisexual users
class GenderlessProfileFilter(django_filters.FilterSet):
    relationship_status = MultipleChoiceFilter(label='', choices=Profile.RELATIONSHIP_STATUS, widget=forms.SelectMultiple(attrs={'title': 'Tình trạng quan hệ ▾'}))
    education = MultipleChoiceFilter(label='', choices=Profile.EDUCATION, widget=forms.SelectMultiple(attrs={'title': 'Học vấn ▾'}))

    
    class Meta:
        model = Profile
        fields = ['relationship_status', 'education']
        labels = {'relationship_status': 'Tình trạng quan hệ', 'education': 'Học vấn'}
