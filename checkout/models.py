from django.db import models
from django.contrib.auth.models import User


class Order(models.Model):
    PLANS = (
        ('plan_one_month', 'Tháng - 200.000đ'),
        ('plan_three_month', '3 Tháng - 300.000đ'),
        ('plan_six_month', '6 Tháng - 400.000đ'),
        )
    plans = models.CharField(choices=PLANS, default='plan_three_month', blank=False, max_length=100)
    full_name = models.CharField(max_length=50, blank=False)
    phone_number = models.CharField(max_length=20, blank=False)
    province = models.CharField(max_length=40, blank=False)
    postcode = models.CharField(max_length=20, blank=True)
    district = models.CharField(max_length=40, blank=False)
    ward = models.CharField(max_length=40, blank=False)
    street = models.CharField(max_length=40, blank=False)
    number = models.CharField(max_length=40, blank=False)
    date = models.DateField()
    
    def __str__(self):
        return "{0}-{1}-{2}".format(self.id, self.date, self.full_name)


class Subscription(models.Model):
    user = models.ForeignKey(User, null=False, on_delete=models.DO_NOTHING)
    plan = models.CharField(max_length=255)
    customer_id = models.CharField(max_length=255)
    