from django import forms
from .models import Order

class MakePaymentForm(forms.Form):
    
    MONTH_CHOICES = [(i,i) for i in range(1,12)]
    YEAR_CHOICES = [(i,i) for i in range(2019, 2036)]
    
    # Required false used to keep secure
    credit_card_number = forms.CharField(label='Thẻ VISA', required=False)
    cvv = forms.CharField(label='Mã bảo mật (CVV)', required=False)
    expiry_month = forms.ChoiceField(label='Ngày hết hạn', choices=MONTH_CHOICES, required=False)
    expiry_year = forms.ChoiceField(label='Năm hết hạn', choices=YEAR_CHOICES, required=False)
    stripe_id = forms.CharField(widget=forms.HiddenInput)
    
class OrderForm(forms.ModelForm):
    
    class Meta:
        model = Order
        fields = ('plans', 'full_name', 'phone_number', 'province', 'postcode', 'district', 'ward', 'street', 'number')
        labels = {'full_name': 'Họ và tên', 'phone_number': 'Số điện thoại', 'province': 'Tỉnh', 'postcode':'Mã bưu điện', 'district':'Quận', 'ward': 'Phường', 'street':'Đường', 'number':'Số nhà'}
