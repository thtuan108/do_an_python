from django.contrib.auth.models import User


class EmailAuth:
    """
    Xác thực đăng nhập bằng email
    """
    
    def authenticate(self, username=None, password=None):
        """
        Xác thực email và mật khẩu
        """
        
        try:
            user = User.objects.get(email=username)
            if user.check_password(password):
                return user
            return None
        except User.DoesNotExist:
            return None
            
    def get_user(self, user_id):
        """
        Xác thực user tồn tại
        """
        
        try:
            user = User.objects.get(pk=user_id)
            if user.is_active:
                return user
            return None
        except User.DoesNotExist:
            return None
