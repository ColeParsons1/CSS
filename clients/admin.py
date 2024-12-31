# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from django.contrib import admin
from .models import Potential
#from friendship.admin import
admin.site.site_header = 'Crafted Site Solutions - Staff Portal' 




class CSSAdminMixin(object):
    class Media:
        css = {
            'all': ('/static/assets/css/soft-design-system.css'),
        }
        
admin.site.register(Potential)		
# Register your models here.
