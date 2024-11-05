# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from django.db import models

class product(models.Model):
    img_main = models.ImageField(blank=True, null=True)
# Create your models here.
