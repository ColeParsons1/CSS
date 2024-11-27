# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from django.contrib import admin
from .models import Item
from .models import Member
#from friendship.admin import
admin.site.site_header = 'TG | Admin Dashboard' 
admin.site.register(Item)
admin.site.register(Member)



class CSSAdminMixin(object):
    class Media:
        css = {
            'all': ('/static/assets/css/soft-design-system.css'),
        }
        
#admin.site.register(admin.ModelAdmin, CSSAdminMixin)		
# Register your models here.