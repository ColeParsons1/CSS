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




class Potential(models.Model):
    Salesman = models.OneToOneField(User, on_delete=models.CASCADE, blank=True, null=True)
    Company = models.CharField(max_length=100, blank=True, null=True)
    Notes = models.TextField(max_length=10000, blank=True, null=True)

    def __str__(self): 
        return self.Company
    
class Confirmed(models.Model):
    Name = models.CharField(max_length=100, blank=True, null=True)
    Phone = models.IntegerField(blank=True, null=True)
    Notes = models.TextField(max_length=10000, blank=True, null=True)

    def __str__(self): 
        return self.Name    
    
#class Payment_Method(models.Model):
    #Member = models.OneToOneField(User, on_delete=models.CASCADE, blank=True, null=True)
    #First_Name = models.CharField(max_length=30, blank=True, null=True)
    #Last_Name = models.CharField(max_length=30, blank=True, null=True)
    #Card_Number = models.IntegerField(blank=True, null=True)
    #Security_Code = models.IntegerField(blank=True, null=True)
    #Billing_Street = models.CharField(max_length=100, blank=True, null=True)

