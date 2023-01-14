from django.db import models
from django.contrib.auth.models import User
from chat.models import Conversations
from checkout.models import Subscription
from django.db.models.signals import post_save, pre_delete
import uuid
import datetime
import os


# Model hồ sơ người dùng
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(max_length=500, default='', blank=False)
    LOOKING_FOR = (
        ('NAM', 'Nam'),
        ('NỮ', 'Nữ'),
        ('BOTH', 'Cả hai'),
    )

    RELATIONSHIP_STATUS = (
        ('ĐỘC THÂN', 'Độc thân'),
        ('ĐÃ KẾT HÔN', 'Đã kết hôn'),
        ('LI HÔN', 'Li hôn'),
    )
    GENDER = (
        ("NAM", "Nam"),
        ("NỮ", "Nữ"))
    EDUCATION = (
    ('THPT', 'THPT'),
    ('CAO ĐẲNG', 'Cao đẳng'),
    ('ĐẠI HỌC', 'Đại học'),
    ('THẠC SĨ', 'Thạc sĩ'),
    ('TIẾN SĨ', 'Tiến sĩ'),
    )

    gender = models.CharField(choices=GENDER, default="NAM", max_length=6)
    relationship_status = models.CharField(choices=RELATIONSHIP_STATUS, default="ĐỘC THÂN", blank=False, max_length=100)
    education = models.CharField(choices=EDUCATION, default="ĐẠI HỌC", blank=False, max_length=100)
    height = models.DecimalField(max_digits=10, default=170, decimal_places=2)
    looking_for = models.CharField(choices=LOOKING_FOR, default='BOTH', blank=False, max_length=6)
    location = models.CharField(max_length=100, default='', blank=False)
    birth_date = models.DateField(null=True, default='1990-01-01', blank=True)
    is_premium = models.BooleanField(default=False)

    def age(self):
        """
            input: thông tin hồ sơ user
            output: số tuổi user
        """
        return int((datetime.date.today() - self.birth_date).days / 365.25)


def image_filename(instance, filename):
    """
        input: tên file
        output: file url
    """
    ext = filename.split('.')[-1]
    filename = "%s.%s" % (uuid.uuid4(), ext)
    return os.path.join('images/', filename)


# Model ảnh hồ sơ
class ProfileImage(models.Model):
    user = models.ForeignKey(User, default=None, on_delete=models.DO_NOTHING)
    image = models.ImageField(upload_to=image_filename, blank=True)

    
def create_user_profile(sender, instance, created, **kwargs):
    """
        input: thông tin hồ sơ
        output: thêm 1 hồ sơ mới hoặc cập nhật lại hồ sơ cũ
    """
    if created:
        Profile.objects.create(user=instance)


post_save.connect(create_user_profile, sender=User)


def save_user_profile(sender, instance, **kwargs):
    """
        Lưu hồ sơ
    """
    instance.profile.save()


post_save.connect(create_user_profile, sender=User)


def pre_delete_user(sender, instance, **kwargs):
    """
        Dọn dẹp hồ sơ, tin nhắn của user trước khi xóa
    """
    conversations = Conversations.objects.filter(participants=instance.id)
    for conversation in conversations:
        conversation.delete()


pre_delete.connect(pre_delete_user, sender=User)
