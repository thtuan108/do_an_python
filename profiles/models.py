from django.db import models
from django.contrib.auth.models import User
from chat.models import Conversations
from checkout.models import Subscription
from django.db.models.signals import post_save, pre_delete
from django.utils.crypto import get_random_string
from django.core.validators import MaxValueValidator, MinValueValidator
import uuid
import datetime
import os
import math
from django.db.models.expressions import RawSQL
import stripe
from django.db.backends.signals import connection_created
from django.dispatch import receiver
import os


"""
Only necessary for local and testing sqlite databases
As SQLite does not support math functions, the following function adds the
capability for it to do so
"""
if "DEVELOPMENT" in os.environ or "TESTING" in os.environ:
    @receiver(connection_created)
    def extend_sqlite(connection=None, **kwargs):
        cf = connection.connection.create_function
        cf('acos', 1, math.acos)
        cf('cos', 1, math.cos)
        cf('radians', 1, math.radians)
        cf('sin', 1, math.sin)


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
        ("MALE", "Nam"),
        ("FEMALE", "Nữ"))
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
    height = models.DecimalField(max_digits=10, default=180.34, decimal_places=2)
    looking_for = models.CharField(choices=LOOKING_FOR, default='BOTH', blank=False, max_length=6)
    location = models.CharField(max_length=100, default='', blank=False)
    birth_date = models.DateField(null=True, default='1990-01-01', blank=True)

    def age(self):
        return int((datetime.date.today() - self.birth_date).days / 365.25  )

def image_filename(instance, filename):
    ext = filename.split('.')[-1]
    filename = "%s.%s" % (uuid.uuid4(), ext)
    return os.path.join('images/', filename)
    
class ProfileImage(models.Model):
    user = models.ForeignKey(User, default=None, on_delete=models.DO_NOTHING)
    image = models.ImageField(upload_to=image_filename, blank=True)

    
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

post_save.connect(create_user_profile, sender=User)
    
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()

post_save.connect(create_user_profile, sender=User)

def pre_delete_user(sender, instance, **kwargs):
    # Before user deleted, delete all conversations they were participants of
    conversations = Conversations.objects.filter(participants=instance.id)
    for conversation in conversations:
        conversation.delete()
    
    # Before user deleted, cancel all subscriptions
    customer = Subscription.objects.filter(user_id=instance.id).first()
    try:
        if customer:
            stripe_customer = stripe.Customer.retrieve(customer.customer_id)
            for sub in stripe_customer.subscriptions.data:
                stripe.Subscription.modify(
                    sub.id,
                    cancel_at_period_end=True
                )
    except:
        print('Pre-delete user failed')
        
pre_delete.connect(pre_delete_user, sender=User)
