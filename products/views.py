# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

import json
import os
import re
import base64
from xml.dom import minidom
import certifi
from django.conf import settings
from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponse
import stripe
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from products.utils import get_product, Product, load_product, load_product_by_slug, load_json_product, load_product_by_id
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from requests.auth import HTTPDigestAuth
import requests
import json
from .forms import IntakeForm
from django.shortcuts import render
from django.shortcuts import render, redirect, get_object_or_404
from django.core.mail import send_mail
from sendsms import api
import math
from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import update_last_login
from django.contrib.auth.hashers import check_password
from django.conf import settings
from django.contrib.auth.backends import BaseBackend
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import logout
from django.http import HttpResponse
from django.http import JsonResponse
#from rest_framework_api_key.permissions import HasAPIKey
import json
import stripe
from django.contrib import messages
from django.contrib.auth.signals import user_logged_in, user_logged_out, user_login_failed
from django.db.models import Q
from django.template import loader
#from django.conf.urls import url
from django.contrib.contenttypes.fields import GenericForeignKey
from django.shortcuts import render, redirect
from .forms import sign
import datetime
import pprint
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_decode
from django.utils.http import urlsafe_base64_encode
from django.template.loader import render_to_string
from django.contrib.auth.forms import PasswordResetForm
from products.tokens import account_activation_token
from django.db.models import Q
from django.shortcuts import render
from django.contrib.contenttypes.models import ContentType
from django.http import HttpResponseRedirect, JsonResponse
from django.views.generic import View
from django.contrib.auth import get_user_model
from operator import and_, or_
import operator
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.csrf import csrf_exempt
from .forms import IntakeForm, sign
from .models import Member
from .models import Item
from django.core.files.storage import FileSystemStorage
from django.views.generic import TemplateView, ListView
from django.utils.decorators import method_decorator
import json
import requests
import urllib.parse
from django.middleware.csrf import get_token
from django.core.mail import BadHeaderError, send_mail
from django.http import HttpResponse, HttpResponseRedirect
import xml.etree.ElementTree as ET
from products import xmltodict
import csv
from bs4 import BeautifulSoup
from requests_html import HTMLSession
import ssl



#from stripe_python import get_products

stripe.api_key = getattr(settings, 'STRIPE_SECRET_KEY')

def load_json(path: str) -> dict:  
    if path.endswith(".json"):
        print(f"> Loading JSON from '{path}'")
        with open(path, mode="r") as open_file:
            content = open_file.read()

        return json.loads(content)
    elif path.endswith(".xml"):
        print(f"> Loading XML as JSON from '{path}'")
        #xml = ET.tostring(ET.parse(path).getroot())
        with open(file=path, mode='r', encoding='utf-8') as xml_txt:
         parser = ET.XMLParser(encoding="utf-8")
         #tree = ET.parse("davidsons_inventory.xml", parser=parser)
         #print(ET.tostring(xml))                 
         #xml = ET.fromstring((xml_txt.read().encode('utf-8')), ET.XMLParser(encoding='utf-8'))
         xml = ET.parse(path, parser = parser)
        #print(xml)
        return xml
    #xmltodict.parse(xml, attr_prefix="@", cdata_key="#text", dict_constructor=dict)

    print(f"> Loading failed for '{path}'")
    return {}

def save_json_to_csv(request):
    # 1. Get the JSON data
    json_data = request.POST.get('json_data', '{}')  # Get JSON from request data
    data = json.loads(json_data)

    # 2. Create a CSV response
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="data.csv"'

    # 3. Write the CSV data
    writer = csv.writer(response)

    # Write header row (if needed)
    if isinstance(data, list) and len(data) > 0:
        writer.writerow(data[0].keys())

    # Write data rows
    for row in data:
        writer.writerow(row.values())

    return response

def load_inventory(request):

    url = "http://api_url"

# It is a good practice not to hardcode the credentials. So ask the user to enter credentials at runtime
    myResponse = requests.get(url,auth=HTTPDigestAuth(raw_input("username: "), raw_input("Password: ")), verify=True)
#print (myResponse.status_code)

# For successful API call, response code will be 200 (OK)
    if(myResponse.ok):

    # Loading the response data into a dict variable
    # json.loads takes in only binary or string variables so using content to fetch binary content
    # Loads (Load String) takes a Json file and converts into python data structure (dict or list, depending on JSON)
     jData = json.loads(myResponse.content)

     print("The response contains {0} properties".format(len(jData)))
     print("\n")
     for key in jData:
        print(key) + " : " + jData[key]
    else:

     myResponse.raise_for_status()

     context = {
        'products': jData,
    }
    
    return render(request, context)

def read_csv(file_path):
    with open('davidsons_inventory.csv', 'r') as file:
        csv_reader = csv.reader(file)
        # Skip the header row if it exists
        next(csv_reader, None)  

        for row in csv_reader:
            # Process each row in the CSV file
            print(row)


@csrf_exempt
def index(request):
    # Collect Products
    products = []
    featured_product = None

    session = HTMLSession()
    response = session.request(method="get",url="https://www.davidsonsinc.com/promotional/weekly-firearm-specials")
    
    if response.status_code != 200:
     print('Could not fetch the page')
     exit(1)

    print('Successfully fetched the page')

    soup = BeautifulSoup(response.content, 'html.parser')
    print(soup)

    data = []
    for item in soup.find_all('div', class_='item'):
        item = item.find('h2').text
        price = item.find('span', class_='price').text
        data.append({'item': item, 'price': price})

    # 2. Create the CSV response
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="data.csv"'

    # 3. Write data to CSV
    writer = csv.writer(response)
    writer.writerow(['Item'])
    for row in data:
        #writer.writerow([row['Item_Number']])
        '''Item.objects.create(Item_Number=row.Item_Number,
                               Item_Description=row.Item_Description, 
                               MSP=row['MSP'], 
                               Retail_Price=row['Retail_Price'], 
                               Dealer_Price=row['Dealer_Price'],
                               Sale_Price=row['Sale_Price'],
                               Qty=row['Quanity'],
                               UPC=row['UPC Code'],
                               Manufacturer=row['Manufacturer'],
                               Gun_Type=row['Gun_Type'], 
                               Model_Series=row['Model_Series'] ,
                               Caliber=row['Caliber'],
                               Action=row['Action_Type'],
                               Capacity=row['Capacity'],
                               Finish=row['Finish'],
                               Stock=row['Stock'],
                               Sights=row['Sights'],
                               Barrel_Length=row['Barrel_Length'],
                               Overall_length=row['Overall_Length'] ,
                               Features=row['Features'])
        Item.save()

    response2 = HttpResponse(content_type='text/csv')
    response2['Content-Disposition'] = 'attachment; filename="data.csv"'

    writer = csv.writer(response2)
    writer.writerow(['Title', 'Price'])
    for row in data:
        #print(row)
        writer.writerow([row['item'], row['price']])

    items = soup.find_all('Item')

    #titles = []
    

     #data_frame = pandas.DataFrame({'Item': items})
     #data_frame.to_csv('items.csv', index=False, encoding='utf-8')
    #response.html.render() '''
    #response = requests.get('https://books.toscrape.com')
    #if  response.status_code != 200:
     #print('Could not fetch the page')
     #exit(1)


    #soup = BeautifulSoup(response.content, 'html.parser')
    #articles = soup.find_all('article')

    #titles = []
    #for article in articles:
      #title = article.h3.a.attrs['title']
      #titles.append(title)

    #data_frame = pandas.DataFrame({'Title': titles})
    #data_frame.to_csv('books.csv', index=False, encoding='utf-8')
    #print('Successfully fetched the page')
    #response = requests.get(
         #"https://www.davidsonsinc.com", params='', verify=False
   # )





    with open('davidsons_inventory.csv', 'r') as file:
        csv_reader = csv.reader(file)
        # Skip the header row if it exists
        next(csv_reader, None)  

        for row in csv_reader:
            # Process each row in the CSV file


            #!this need to be added to the db!!!!!!!!!!
            #print(row)
            products.append( row )
            #product.objects.create(Item_Number=row['Item_Number'])
            #product.save()
            i=Item.objects.all()
            i.delete()
            '''Item.objects.create(Item_Number=row[0],
                               Item_Description=row[1], 
                               MSP=row[2], 
                               Retail_Price=row[3], 
                               Dealer_Price=row[4],
                               Sale_Price=row[5],
                               Sale_Ends=row[6],
                               Qty=row[7],
                               UPC=row[8],
                               Manufacturer=row[9],
                               Gun_Type=row[10], 
                               Model_Series=row[11],
                               Caliber=row[12],
                               Action=row[13],
                               Capacity=row[14],
                               Finish=row[15],
                               Stock=row[16],
                               Sights=row[17],
                               Barrel_length=row[18],
                               Overall_length=row[19],
                               Features=row[20])
                                
                                
                                
            #Member.save()
            '''
    #xmldoc = minidom.parse('davidsons_inventory.xml')
    #root = xmldoc.getroot()
    #elements = []
    #tree = ET.parse('your_data.xml')
    #xml_data = xmldoc.getroot()
    #xmlstr = ET.tostring(xml_data, encoding='utf-8', method='xml')
    #response = xmltodict.parse(xmlstr.text.replace('\x07', ''))
    #data_dict = dict(xmltodict.parse(xmlstr))
    #path = "davidsons_inventory.xml"

    
    #xml = u"""<?xml version='1.0' encoding='utf-8'?>
    #<osm generator="pycrocosm server" version="0.6"><changeset created_at="2017-09-06T19:26:50.302136+00:00" id="273" max_lat="0.0" max_lon="0.0" min_lat="0.0" min_lon="0.0" open="true" uid="345" user="john"><tag k="test" v="Съешь же ещё этих мягких французских булок да выпей чаю" /><tag k="foo" v="bar" /><discussion><comment data="2015-01-01T18:56:48Z" uid="1841" user="metaodi"><text>Did you verify those street names?</text></comment></discussion></changeset></osm>"""

    #xmltest = ET.fromstring(response.encode("utf-8"))
    #data = load_json(path)
    #print(xmltest)
    #print(json.dumps(data, indent=2))
    #for item in root.findall('Item'):
        #root = ET.fromstring(item_desc)
        #name = country.get('bit')
        #elements.append(item)
        

    # Scan all JSONs in `templates/products`
    for aJsonPath in get_product():  
        if 'featured.json' in aJsonPath:
            continue

        # Load the product info from JSON
        product = load_product( aJsonPath )
        
        # Is Valid? Save the object
        if product:     
            products.append( product )
    
    context = {
        'featured': load_product_by_slug('featured'),
        'products': products,
        'form': IntakeForm,
    }
    return render(request, 'ecommerce/index.html', context)

@csrf_exempt
def email_tg(request):
    subject = request.POST.get("subject", "Membership follow up")
    message = request.POST.get("message", "")

    from_email = request.POST.get("from_email", "info@tacticalgentlemensft.com")
    if subject and message and from_email:
        try:
            send_mail(subject, message, from_email, ["info@tacticalgentlemensft.com"])
        except BadHeaderError:
            return HttpResponse("Invalid header found.")
        return HttpResponseRedirect("/contact/thanks/")
    else:
        # In reality we'd use a form class
        # to get proper validation errors.
        return HttpResponse("Make sure all fields are entered and valid.")
    
@csrf_exempt
def send_email(request):
    subject = request.POST.get("subject", "Tactical Gentlemen Members Club")
    message = request.POST.get("message", "Join the Tactical Gentlemen Members Club today for exclusive benefits and unparalleled access to a world of precision and skill. As a member, you'll enjoy priority registration for events, special discounts on training courses, and access to a community of like-minded enthusiasts. Our club offers regular meet-ups, competitions, and expert-led workshops designed to enhance your knowledge and proficiency. Whether you're a seasoned marksman or new to the world of firearms, our club provides a supportive environment to learn and grow. Don't miss out on this unique opportunity—register now and elevate your firearms experience to the next level!")
    from_email = request.POST.get("from_email", "info@tacticalgentlemensft.com")
    to_email = request.POST.get("email", "email")

    #message.Subject = "An HTML Email"
    Html = """<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:v="urn:schemas-microsoft-com:vml" xmlns:o="urn:schemas-microsoft-com:office:office"><head><meta http-equiv="Content-Type" content="text/html; charset=utf-8"><meta http-equiv="X-UA-Compatible" content="IE=edge"><meta name="format-detection" content="telephone=no"><meta name="viewport" content="width=device-width, initial-scale=1.0"><title>Membership Email</title><style type="text/css" emogrify="no">#outlook a { padding:0; } .ExternalClass { width:100%; } .ExternalClass, .ExternalClass p, .ExternalClass span, .ExternalClass font, .ExternalClass td, .ExternalClass div { line-height: 100%; } table td { border-collapse: collapse; mso-line-height-rule: exactly; } .editable.image { font-size: 0 !important; line-height: 0 !important; } .nl2go_preheader { display: none !important; mso-hide:all !important; mso-line-height-rule: exactly; visibility: hidden !important; line-height: 0px !important; font-size: 0px !important; } body { width:100% !important; -webkit-text-size-adjust:100%; -ms-text-size-adjust:100%; margin:0; padding:0; } img { outline:none; text-decoration:none; -ms-interpolation-mode: bicubic; } a img { border:none; } table { border-collapse:collapse; mso-table-lspace:0pt; mso-table-rspace:0pt; } th { font-weight: normal; text-align: left; } *[class="gmail-fix"] { display: none !important; } </style><style type="text/css" emogrify="no"> @media (max-width: 600px) { .gmx-killpill { content: ' \03D1';} } </style><style type="text/css" emogrify="no">@media (max-width: 600px) { .gmx-killpill { content: ' \03D1';} .r0-o { border-style: solid !important; margin: 0 auto 0 auto !important; width: 320px !important } .r1-i { background-color: #ffffff !important } .r2-c { box-sizing: border-box !important; text-align: center !important; valign: top !important; width: 100% !important } .r3-o { border-style: solid !important; margin: 0 auto 0 auto !important; width: 100% !important } .r4-i { padding-bottom: 20px !important; padding-left: 15px !important; padding-right: 15px !important; padding-top: 20px !important } .r5-c { box-sizing: border-box !important; display: block !important; valign: top !important; width: 100% !important } .r6-o { border-style: solid !important; width: 100% !important } .r7-i { padding-left: 0px !important; padding-right: 0px !important } .r8-c { box-sizing: border-box !important; padding-bottom: 15px !important; padding-top: 15px !important; text-align: left !important; valign: top !important; width: 100% !important } .r9-i { background-color: #ffffff !important; padding-bottom: 20px !important; padding-left: 15px !important; padding-right: 15px !important; padding-top: 20px !important } .r10-i { padding-bottom: 20px !important; padding-left: 0px !important; padding-right: 0px !important; padding-top: 20px !important } .r11-i { background-color: #eff2f7 !important; padding-bottom: 20px !important; padding-left: 15px !important; padding-right: 15px !important; padding-top: 20px !important } .r12-c { box-sizing: border-box !important; text-align: left !important; valign: top !important; width: 100% !important } .r13-o { border-style: solid !important; margin: 0 auto 0 0 !important; width: 100% !important } .r14-i { padding-bottom: 0px !important; padding-top: 15px !important; text-align: center !important } .r15-i { padding-bottom: 0px !important; padding-top: 0px !important; text-align: center !important } .r16-i { padding-bottom: 15px !important; padding-top: 15px !important; text-align: center !important } body { -webkit-text-size-adjust: none } .nl2go-responsive-hide { display: none } .nl2go-body-table { min-width: unset !important } .mobshow { height: auto !important; overflow: visible !important; max-height: unset !important; visibility: visible !important } .resp-table { display: inline-table !important } .magic-resp { display: table-cell !important } } </style><!--[if !mso]><!--><style type="text/css" emogrify="no">@import url("https://fonts.googleapis.com/css2?family=Open Sans"); </style><!--<![endif]--><style type="text/css">p, h1, h2, h3, h4, ol, ul, li { margin: 0; } a, a:link { color: #4aab48; text-decoration: underline } .nl2go-default-textstyle { color: #3b3f44; font-family: arial,helvetica,sans-serif; font-size: 16px; line-height: 1.5; word-break: break-word } .default-button { color: #ffffff; font-family: arial,helvetica,sans-serif; font-size: 16px; font-style: normal; font-weight: normal; line-height: 1.15; text-decoration: none; word-break: break-word } .default-heading1 { color: #1F2D3D; font-family: Open Sans, arial; font-size: 36px; word-break: break-word } .default-heading2 { color: #1F2D3D; font-family: Open Sans, arial; font-size: 32px; word-break: break-word } .default-heading3 { color: #1F2D3D; font-family: Open Sans, arial; font-size: 24px; word-break: break-word } .default-heading4 { color: #1F2D3D; font-family: Open Sans, arial; font-size: 18px; word-break: break-word } a[x-apple-data-detectors] { color: inherit !important; text-decoration: inherit !important; font-size: inherit !important; font-family: inherit !important; font-weight: inherit !important; line-height: inherit !important; } .no-show-for-you { border: none; display: none; float: none; font-size: 0; height: 0; line-height: 0; max-height: 0; mso-hide: all; overflow: hidden; table-layout: fixed; visibility: hidden; width: 0; } </style><!--[if mso]><xml> <o:OfficeDocumentSettings> <o:AllowPNG/> <o:PixelsPerInch>96</o:PixelsPerInch> </o:OfficeDocumentSettings> </xml><![endif]--><style type="text/css">a:link{color: #4aab48; text-decoration: underline;}</style></head><body bgcolor="#ffffff" text="#3b3f44" link="#4aab48" yahoo="fix" style="background-color: #ffffff;"> <table cellspacing="0" cellpadding="0" border="0" role="presentation" class="nl2go-body-table" width="100%" style="background-color: #ffffff; width: 100%;"><tr><td> <table cellspacing="0" cellpadding="0" border="0" role="presentation" width="600" align="center" class="r0-o" style="table-layout: fixed; width: 600px;"><tr><td valign="top" class="r1-i" style="background-color: #ffffff;"> <table cellspacing="0" cellpadding="0" border="0" role="presentation" width="100%" align="center" class="r3-o" style="table-layout: fixed; width: 100%;"><tr><td class="r4-i" style="padding-bottom: 20px; padding-top: 20px;"> <table width="100%" cellspacing="0" cellpadding="0" border="0" role="presentation"><tr><th width="100%" valign="top" class="r5-c" style="font-weight: normal;"> <table cellspacing="0" cellpadding="0" border="0" role="presentation" width="100%" class="r6-o" style="table-layout: fixed; width: 100%;"><tr><td valign="top" class="r7-i" style="padding-left: 15px; padding-right: 15px;"> <table width="100%" cellspacing="0" cellpadding="0" border="0" role="presentation"><tr><td class="r8-c nl2go-default-textstyle" align="left" style="color: #3b3f44; font-family: arial,helvetica,sans-serif; font-size: 16px; line-height: 1.5; word-break: break-word; padding-bottom: 15px; padding-top: 15px; text-align: left; valign: top;"> <div><p style="margin: 0;">Join the Tactical Gentlemen Members Club today for exclusive benefits and unparalleled access to a world of precision and skill. As a member, you'll enjoy priority registration for events, special discounts on training courses, and access to a community of like-minded enthusiasts. Our club offers regular meet-ups, competitions, and expert-led workshops designed to enhance your knowledge and proficiency. Whether you're a seasoned marksman or new to the world of firearms, our club provides a supportive environment to learn and grow. Don't miss out on this unique opportunity—register now and elevate your firearms experience to the next level!</p></div> </td> </tr></table></td> </tr></table></th> </tr></table></td> </tr></table><table cellspacing="0" cellpadding="0" border="0" role="presentation" width="100%" align="center" class="r3-o" style="table-layout: fixed; width: 100%;"><tr><td class="r9-i" style="background-color: #ffffff; padding-bottom: 20px; padding-top: 20px;"> <table width="100%" cellspacing="0" cellpadding="0" border="0" role="presentation"><tr><th width="100%" valign="top" class="r5-c" style="font-weight: normal;"> <table cellspacing="0" cellpadding="0" border="0" role="presentation" width="100%" class="r6-o" style="table-layout: fixed; width: 100%;"><tr><td valign="top" class="r7-i" style="padding-left: 15px; padding-right: 15px;"> <table width="100%" cellspacing="0" cellpadding="0" border="0" role="presentation"><tr><td class="r2-c" align="center"> <table cellspacing="0" cellpadding="0" border="0" role="presentation" width="200" class="r3-o" style="table-layout: fixed; width: 200px;"><tr><td style="font-size: 0px; line-height: 0px;"> <img src="https://img.mailinblue.com/7798643/images/content_library/original/673282c9d098a0978a3f4750.jpg" width="200" border="0" style="display: block; width: 100%;"></td> </tr></table></td> </tr></table></td> </tr></table></th> </tr></table></td> </tr></table><table cellspacing="0" cellpadding="0" border="0" role="presentation" width="100%" align="center" class="r3-o" style="table-layout: fixed; width: 100%;"><tr><td class="r10-i" style="padding-bottom: 20px; padding-top: 20px;"> <table width="100%" cellspacing="0" cellpadding="0" border="0" role="presentation"><tr><th width="50%" valign="top" class="r5-c" style="font-weight: normal;"> <table cellspacing="0" cellpadding="0" border="0" role="presentation" width="100%" class="r6-o" style="table-layout: fixed; width: 100%;"><tr><td valign="top" class="r7-i" style="padding-left: 15px; padding-right: 15px;"> <table width="100%" cellspacing="0" cellpadding="0" border="0" role="presentation"></table></td> </tr></table></th> <th width="50%" valign="top" class="r5-c" style="font-weight: normal;"> <table cellspacing="0" cellpadding="0" border="0" role="presentation" width="100%" class="r6-o" style="table-layout: fixed; width: 100%;"><tr><td valign="top" class="r7-i" style="padding-left: 15px; padding-right: 15px;"> <table width="100%" cellspacing="0" cellpadding="0" border="0" role="presentation"></table></td> </tr></table></th> </tr></table></td> </tr></table><table cellspacing="0" cellpadding="0" border="0" role="presentation" width="100%" align="center" class="r3-o" style="table-layout: fixed; width: 100%;"><tr><td class="r11-i" style="background-color: #eff2f7; padding-bottom: 20px; padding-top: 20px;"> <table width="100%" cellspacing="0" cellpadding="0" border="0" role="presentation"><tr><th width="100%" valign="top" class="r5-c" style="font-weight: normal;"> <table cellspacing="0" cellpadding="0" border="0" role="presentation" width="100%" class="r6-o" style="table-layout: fixed; width: 100%;"><tr><td valign="top" class="r7-i" style="padding-left: 15px; padding-right: 15px;"> <table width="100%" cellspacing="0" cellpadding="0" border="0" role="presentation"><tr><td class="r12-c" align="left"> <table cellspacing="0" cellpadding="0" border="0" role="presentation" width="100%" class="r13-o" style="table-layout: fixed; width: 100%;"><tr><td align="center" valign="top" class="r14-i nl2go-default-textstyle" style="color: #3b3f44; font-family: arial,helvetica,sans-serif; word-break: break-word; font-size: 18px; line-height: 1.5; padding-top: 15px; text-align: center;"> <div><p style="margin: 0;"><span style="font-family: 'open sans', Arial;">Tactical Gentlemen</span></p></div> </td> </tr></table></td> </tr><tr><td class="r12-c" align="left"> <table cellspacing="0" cellpadding="0" border="0" role="presentation" width="100%" class="r13-o" style="table-layout: fixed; width: 100%;"><tr><td align="center" valign="top" class="r14-i nl2go-default-textstyle" style="color: #3b3f44; font-family: arial,helvetica,sans-serif; word-break: break-word; font-size: 18px; line-height: 1.5; padding-top: 15px; text-align: center;"> <div><p style="margin: 0; font-size: 14px;">This email was sent to {{contact.EMAIL}}</p></div> </td> </tr></table></td> </tr><tr><td class="r12-c" align="left"> <table cellspacing="0" cellpadding="0" border="0" role="presentation" width="100%" class="r13-o" style="table-layout: fixed; width: 100%;"><tr><td align="center" valign="top" class="r15-i nl2go-default-textstyle" style="color: #3b3f44; font-family: arial,helvetica,sans-serif; word-break: break-word; font-size: 18px; line-height: 1.5; text-align: center;"> <div></div> </td> </tr></table></td> </tr><tr><td class="r12-c" align="left"> <table cellspacing="0" cellpadding="0" border="0" role="presentation" width="100%" class="r13-o" style="table-layout: fixed; width: 100%;"><tr><td align="center" valign="top" class="r16-i nl2go-default-textstyle" style="color: #3b3f44; font-family: arial,helvetica,sans-serif; word-break: break-word; font-size: 18px; line-height: 1.5; padding-bottom: 15px; padding-top: 15px; text-align: center;"> <div><p style="margin: 0; font-size: 14px;"> <a href="{{ unsubscribe }}" style="color: #4aab48; text-decoration: underline;">Unsubscribe</a></p></div> </td> </tr></table></td> </tr></table></td> </tr></table></th> </tr></table></td> </tr></table></td> </tr></table></td> </tr></table></body></html>
"""
    #message.Body = """This is alternate text."""


    #send_mail(message)


    if to_email:
        try:
            send_mail(subject, Html, from_email, [to_email])
            Member.objects.create(User=request.user, Email = to_email)
            email_tg(request)
            return HttpResponse('<script>history.back();</script>')
        except BadHeaderError:
            return HttpResponse("Invalid header found.")
        return HttpResponseRedirect("/contact/thanks/")
    else:
        # In reality we'd use a form class
        # to get proper validation errors.
        return HttpResponse("Make sure all fields are entered and valid.")    

def signup(request):
    if request.method == 'POST':
        form = sign(request.POST)
        if form.is_valid():
            user = form.save()
            user.refresh_from_db()
            #user.profile.birth_date = form.cleaned_data.get('birth_date')
            user.is_staff = False
            user.is_superuser = False
            user.is_admin = False
            user.save()
            current_site = get_current_site(request)
            subject = 'Activate Your Purefun Account'
            message = render_to_string('main/account_activation_email.html', {
                'user': user,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': account_activation_token.make_token(user),
            })
            login(request, user)
            user.email_user(subject, message)
            return render(request, 'main/account_activation_sent.html')
    else:
        form = sign()
    return render(request, 'main/signup.html', {'form': form})


def activate(request, uidb64, token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = user.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.Profile.email_confirmed = True
        user.save()
        login(request, user)
        return redirect('index')
    else:
        return render(request, 'main/account_activation_invalid.html')

@csrf_exempt        
def account_activation_sent(request):
    

    send_email(request)
    return HttpResponse('<script>history.back();</script>')


def account_activation_email(request):
    return render(request, 'activate')

def activate(request, uidb64, token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = user.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.Profile.email_confirmed = True
        user.save()
        login(request, user)
        return redirect('index')
    else:
        return render(request, 'main/account_activation_invalid.html')    


def login_user(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)
                return render(request, 'main/login.html', {'albums': albums})
            else:
                return render(request, 'main/login.html', {'error_message': 'Your account has been disabled'})
        else:
            return render(request, 'main/login.html', {'error_message': 'Invalid login'})
    return render(request, 'main/login.html')

def product_details(request, slug):
    try:
        product = load_product_by_slug( slug )
        STRIPE_IS_ACTIVE = getattr(settings, 'STRIPE_IS_ACTIVE')

        context = { 
            'product': product,
            'STRIPE_IS_ACTIVE': STRIPE_IS_ACTIVE
        }
        return render(request, 'ecommerce/template.html', context)
    except:
        return redirect('/page404')

def get_publishable_key(request):
    stripe_config = {"publicKey": getattr(settings, 'STRIPE_PUBLISHABLE_KEY')}
    return JsonResponse(stripe_config)

def success(request):
    return render(request, "ecommerce/payment-success.html")

def cancelled(request):
    return render(request, "ecommerce/payment-cancelled.html")

def create_checkout_session(request, slug):
    product = load_product_by_slug( slug )
    domain_url = getattr(settings, 'DOMAIN_URL')
    stripe.api_key = getattr(settings, 'STRIPE_SECRET_KEY')

    try:
        # Create new Checkout Session for the order
        # Other optional params include:
        # [billing_address_collection] - to display billing address details on the page
        # [customer] - if you have an existing Stripe Customer ID
        # [payment_intent_data] - lets capture the payment later
        # [customer_email] - lets you prefill the email input in the form
        # For full details see https:#stripe.com/docs/api/checkout/sessions/create

        # ?session_id={CHECKOUT_SESSION_ID} means the redirect will have the session ID set as a query param
        checkout_session = stripe.checkout.Session.create(
            success_url=domain_url + "success?session_id={CHECKOUT_SESSION_ID}",
            cancel_url=domain_url + "cancelled",
            payment_method_types=["card"],
            mode="payment",
            line_items=[
                {
                    "name": product.name,
                    "quantity": 1,
                    "currency": product.currency,
                    "amount": int(float(product.price) * 100),
                },
            ],
        )
        return JsonResponse({"sessionId": checkout_session["id"]})
    except Exception as e:
        return JsonResponse(error=str(e)), 403

@staff_member_required
def load_product_json(request):
         
    json_data = []
    context   = {}
    
    try: 

        if not stripe.api_key:
            raise Exception('Stripe secrets not provided in ENV.')

        # load stripe product
        if request.method == "POST":
            products = stripe.Product.list(expand = ['data.default_price'])
            productdict = []
            for product in products:
                dict= {}
                dict['id'] = product['id']
                dict['name'] = product['name']
                dict['price'] = product["default_price"]["unit_amount"]/100
                dict['currency'] = product["default_price"]["currency"]
                dict['full_description'] = product["description"]
                dict['info'] = product["description"][0:30]

                for index, image in enumerate(product['images']):
                    dict['img_main'] = image

                dict['img_card'] = ''
                dict['img_1'] = ''
                dict['img_2'] = ''
                dict['img_3'] = ''

                productdict.append(dict)
            
            for product in productdict:
                json_product = json.dumps( product, indent=4, separators=(',', ': ') )
                json_data.append(json_product)

        # load local product
        local_products = []
        for aJsonPath in get_product():  
            if 'featured.json' in aJsonPath:
                continue
            local_json = load_json_product(aJsonPath)
            local_products.append(json.dumps( local_json, indent=4, separators=(',', ': ') ))


        context['productdict'] = json_data
        context['local_products'] = local_products

    except Exception as e:

        errInfo = str(e)
        context['error'] = errInfo

    # Serve the page to the user
    return render(request, 'ecommerce/create-product.html', context)

@staff_member_required
def create_new_product(request):
    if request.method == 'POST':
        product = request.POST.get('product')
        name = json.loads(product)['name']
        slug = name.lower().replace(' ', '-')

        try:
            products = load_product_by_slug( slug )
            if products:
                return redirect('/load-product')
        except:
            outputFile = f'products/templates/products/{slug}.json'
            with open(outputFile, "w") as outfile: 
                outfile.write( product )
                messages.success(request, "Product added successfully!")
                outfile.close()
            return redirect('/load-product')
    else:
        return redirect('/load-product')


@staff_member_required
def update_product(request, slug):
    if request.method == 'POST':
        product = request.POST.get('product')
        featured = request.POST.get('featured')


        # main image
        main_image = request.FILES.get('main_image', "")
        main_img = ''
        if main_image:
            main_img = base64.b64encode(main_image.read()).decode()
        elif request.POST.get('main_img_link'):
            main_img = request.POST.get('main_img_link')
        else:
            main_img = json.loads(product)['img_main']

        
        # card image
        card_image = request.FILES.get('card_image', "")
        card_img = ''
        if card_image:
            card_img = base64.b64encode(card_image.read()).decode()
        elif request.POST.get('card_img_link'):
            card_img = request.POST.get('card_img_link')
        else:
            card_img = json.loads(product)['img_card']
        
        # image 1
        image_1 = request.FILES.get('image_1', "")
        img_1 = ''
        if image_1:
            img_1 = base64.b64encode(image_1.read()).decode()
        elif request.POST.get('img1_link'):
            img_1 = request.POST.get('img1_link')
        else:
            img_1 = json.loads(product)['img_1']

        # image 2
        image_2 = request.FILES.get('image_2', "")
        img_2 = ''
        if image_2:
            img_2 = base64.b64encode(image_2.read()).decode()
        elif request.POST.get('img2_link'):
            img_2 = request.POST.get('img2_link')
        else:
            img_2 = json.loads(product)['img_2']

        # image 3
        image_3 = request.FILES.get('image_3', "")
        img_3 = ''
        if image_3:
            img_3 = base64.b64encode(image_3.read()).decode()
        elif request.POST.get('img3_link'):
            img_3 = request.POST.get('img3_link')
        else:
            img_3 = json.loads(product)['img_3']

        prod = {
            'id': json.loads(product)['id'],
            'name': json.loads(product)['name'],
            'currency': json.loads(product)['currency'],
            'price': request.POST.get('price'),
            'full_description': request.POST.get('full_description'),
            'info': request.POST.get('info'),
            'img_main': main_img,
            'img_card': card_img,
            'img_1': img_1,
            'img_2': img_2,
            'img_3': img_3,
        }

        try:
            if featured:
                outputFile = f'products/templates/products/featured.json'
            else:
                outputFile = f'products/templates/products/{slug}.json'

            with open(outputFile, "r+") as outfile:
                outfile.seek(0)
                outfile.write(json.dumps(prod, indent=4, separators=(',', ': ')))
                messages.success(request, 'Product updated!')
                outfile.truncate()
            return redirect('/load-product')
        except:
            messages.error(request, "You can't update product id or name!")
            return redirect('/load-product')  
    else:
        return redirect('/load-product')


@staff_member_required
def delete_product(request, slug):
    try:
        outputFile = f'products/templates/products/{slug}.json'
        os.remove(outputFile)
        messages.success(request, "Product Deleted!")
        return redirect('/load-product')
    except:
        messages.error(request, "You can't delete the product.")
        return redirect('/load-product')  


# pages

def presentation(request):
    return render(request, 'pages/index.html')

def about_us(request):
    return render(request, 'pages/page-about-us.html')

def contact_us(request):
    return render(request, 'pages/page-contact-us.html')

def author(request):
    return render(request, 'pages/page-author.html')

def signin(request):
    return render(request, 'pages/page-sign-in.html')

def signup(request):
    return render(request, 'pages/page-sign-up.html')

def page404(request):
    return render(request, 'pages/page-404.html')

# blocks

def page_header(request):
    return render(request, 'pages/page-sections-hero-sections.html')

def features(request):
    return render(request, 'pages/page-sections-features.html')

def navbars(request):
    return render(request, 'pages/navigation-navbars.html')

def navtabs(request):
    return render(request, 'pages/navigation-nav-tabs.html')

def paginations(request):
    return render(request, 'pages/navigation-pagination.html')

def input_areas(request):
    return render(request, 'pages/input-areas-inputs.html')

def input_forms(request):
    return render(request, 'pages/input-areas-forms.html')

def alerts(request):
    return render(request, 'pages/attention-catchers-alerts.html')

def modals(request):
    return render(request, 'pages/attention-catchers-modals.html')

def tooltips(request):
    return render(request, 'pages/attention-catchers-tooltips-popovers.html')

def buttons(request):
    return render(request, 'pages/elements-buttons.html')

def avatars(request):
    return render(request, 'pages/elements-avatars.html')

def dropdowns(request):
    return render(request, 'pages/elements-dropdowns.html')

def toggles(request):
    return render(request, 'pages/elements-toggles.html')

def breadcrumbs(request):
    return render(request, 'pages/elements-breadcrumbs.html')

def badges(request):
    return render(request, 'pages/elements-badges.html')

def typography(request):
    return render(request, 'pages/elements-typography.html')

def progressbar(request):
    return render(request, 'pages/elements-progress-bars.html')
