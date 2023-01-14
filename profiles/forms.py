from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.core.exceptions import ValidationError
from .models import Profile, ProfileImage
from chat.models import Messages
from dating_app import settings

class UserLoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)

class MyUserCreationForm(UserCreationForm):

    def __init__(self, *args, **kwargs):
        super(MyUserCreationForm, self).__init__(*args, **kwargs)

        self.fields['email'].required = True


class UserRegistrationForm(UserCreationForm):
    username = forms.CharField(label="Tên người dùng", widget=forms.TextInput(attrs={'maxlength':'12'}))
    password1 = forms.CharField(label="Nhập mật khẩu", widget=forms.PasswordInput)
    password2 = forms.CharField(label="Xác nhận mật khẩu", widget=forms.PasswordInput)
    
    def __init__(self, *args, **kwargs):
        super(UserRegistrationForm, self).__init__(*args, **kwargs)
        
        self.fields['email'].required = True

        for fieldname in ['username', 'password1', 'password2']:
            self.fields[fieldname].help_text = None
    
    class Meta:
        model = User
        fields = ['email', 'username', 'password1', 'password2']
        labels = {'email': 'Địa chỉ email', 'username': 'Tên người dùng', 'password1': 'Mật khẩu', 'password2': 'Xác nhận mật khẩu'}
        
    def cleaned_email(self):
        """
        Lấy email và username từ form đăng ký
        """
        email = self.cleaned_data.get('email')
        username = self.cleaned_data.get('username')
        if User.objects.filter(email=email).exclude(username=username):
            raise forms.ValidationError(u'Email đã được dùng đăng ký tài khoản. Vui lòng sử dụng email khác.')
    

        return email
    
    def cleaned_password2(self):
        """
        Lấy mật khẩu từ form đăng ký và thực hiện thao tác xác thực
        """
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        
        if not password1 or password2:
            raise ValidationError("Mật khẩu không được bỏ trống")
            
        if password1 != password2:
            raise ValidationError("mật khẩu không khớp. Vui lòng thử lại")
            
        return password2    


class EditProfileForm(UserChangeForm):
    password = None
    confirm_password = forms.CharField(label="Mật khẩu xác nhận", widget=forms.PasswordInput)

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user',None)
        super(EditProfileForm, self).__init__(*args, **kwargs)
        
        for fieldname in ['confirm_password', 'username']:
            self.fields[fieldname].help_text = None

    class Meta:
        model = User
        fields = ('email', 'username')
        labels = {'email': 'Địa chỉ email', 'username': 'Tên người dùng'}

        
class ProfileForm(forms.ModelForm):
    
    HEIGHT_CHOICES = (
        ('150.00', '150 cm'),
        ('155.00', '155 cm'),
        ('160.00', '160 cm'),
        ('165.00', '165 cm'),
        ('170.00', '170 cm'),
        ('175.00', '175 cm'),
        ('180.00', '180 cm'),
        ('185.00', '185 cm'),
        ('190.00', '190 cm'),
    )

    location = forms.CharField(label='Địa chỉ', max_length=100, widget=forms.TextInput(attrs={'id':'autocomplete'}), required=True)
    bio = forms.CharField(label='Mô tả', widget=forms.Textarea(attrs={'class': 'bio-field', 'maxlength': '200'}), required=True)
    birth_date = forms.DateTimeField(label='Ngày sinh', input_formats=settings.DATE_INPUT_FORMATS)
    height = forms.ChoiceField(label='Chiều cao', choices=HEIGHT_CHOICES, initial='', widget=forms.Select(), required=True)
    
    class Meta:
        model = Profile
        fields = ('bio', 'gender', 'relationship_status', 'looking_for', 'education', 'height', 'location', 'birth_date')
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'})
        }
        labels = {'bio': 'Mô tả', 'gender': 'Giới tính', 'relationship_status': 'Tình trạng hôn nhân', 'looking_for': 'Đối tượng tìm kiếm', 'education': 'Học vấn',
                  'height': 'Chiều cao', 'location': 'Địa chỉ', 'birth_date': 'Ngày sinh'}

class ProfileImageForm(forms.ModelForm):
    
    image = forms.ImageField(label='', required=False, error_messages = {'invalid':"Image files only"}, widget=forms.FileInput(attrs = {'class': "profile-photo-input"}))

    class Meta:
        model = ProfileImage
        fields = ('image', )
        
class MessagesForm(forms.ModelForm):
    # message_content = forms.CharField(widget=forms.TextInput)
    
    class Meta:
        model = Messages
        fields = ('message_content', )
        labels = {'message_content': 'Nội dung tin nhắn'}
