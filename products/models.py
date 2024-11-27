# -*- encoding: utf-8 -*-

from django.db import models
from django.conf import settings
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.auth.models import AbstractUser
from django.contrib.auth import get_user_model
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
#from .forms import PostForm
#from .forms import CommentForm
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.contrib.contenttypes.fields import GenericRelation
from django.contrib.contenttypes.models import ContentType
from decimal import Decimal
from warnings import warn
from django.conf import settings
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
#from django.utils.translation import ugettext as _

class Item(models.Model):
    Item_Number = models.CharField(max_length=30, blank=True, null=True)
    img_main = models.ImageField(blank=True, null=True)
    Item_Description = models.CharField(max_length=30, blank=True, null=True)
    MSP = models.CharField(max_length=30, blank=True, null=True)
    Retail_Price = models.CharField(max_length=30, blank=True, null=True)
    Dealer_Price = models.CharField(max_length=30, blank=True, null=True)
    Sale_Price = models.CharField(max_length=30, blank=True, null=True)
    Sale_Ends = models.CharField(max_length=30, blank=True, null=True)
    Qty = models.CharField(max_length=10000, blank=True, null=True)
    UPC = models.CharField(max_length=30, blank=True, null=True)
    Manufacturer = models.CharField(max_length=30, blank=True, null=True)
    Gun_Type = models.CharField(max_length=30, blank=True, null=True)
    Sale_Price = models.CharField(max_length=30, blank=True, null=True)
    Model_Series = models.CharField(max_length=10000, blank=True, null=True)
    Caliber = models.CharField(max_length=10000, blank=True, null=True)
    Action = models.CharField(max_length=10000, blank=True, null=True)
    Capacity = models.CharField(max_length=30, blank=True, null=True)
    Finish = models.CharField(max_length=30, blank=True, null=True)
    Stock = models.CharField(max_length=30, blank=True, null=True)
    Sights = models.CharField(max_length=10000, blank=True, null=True)
    Barrel_length = models.CharField(max_length=10000, blank=True, null=True)
    Overall_length = models.CharField(max_length=30, blank=True, null=True)
    Features = models.CharField(max_length=30, blank=True, null=True)

    def __str__(self): 
        return self.Item_Number + " | " + self.Item_Description
    #img_main = models.ImageField(blank=True, null=True)
#"Item #",
# "Item Description",
# MSP,
# "Retail Price",
# "Dealer Price",
# "Sale Price",
# "Sale Ends",
# Quantity,
# "UPC Code",
# Manufacturer,
# "Gun Type",
# "Model Series",
# Caliber,
# Action,
# Capacity,
# Finish,
# Stock,
# Sights,
# "Barrel Length",
# "Overall Length",
# Features


class Member(models.Model):
    User = models.OneToOneField(User, on_delete=models.CASCADE, blank=True, null=True)
    Email = models.CharField(max_length=100, blank=True, null=True)
    Member_Since = models.DateTimeField(auto_now_add=True)

    def __str__(self): 
        return self.Email
    
#class Payment_Method(models.Model):
    #Member = models.OneToOneField(User, on_delete=models.CASCADE, blank=True, null=True)
    #First_Name = models.CharField(max_length=30, blank=True, null=True)
    #Last_Name = models.CharField(max_length=30, blank=True, null=True)
    #Card_Number = models.IntegerField(blank=True, null=True)
    #Security_Code = models.IntegerField(blank=True, null=True)
    #Billing_Street = models.CharField(max_length=100, blank=True, null=True)

