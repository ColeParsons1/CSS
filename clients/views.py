# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

import json
import os
import re
import base64
import certifi
from django.conf import settings
from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponse
import stripe
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from clients.utils import get_product, Product, load_product, load_product_by_slug, load_json_product, load_product_by_id
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
from rest_framework_api_key.permissions import HasAPIKey
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
from .models import Potential
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
from clients.tokens import account_activation_token
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
import csv
from bs4 import BeautifulSoup
from requests_html import HTMLSession
import ssl
import re
    
MOBILE_AGENT_RE = re.compile(r".*(iphone|mobile|androidtouch)", re.IGNORECASE)


def is_mobile(request):
    """Return True if the request comes from a mobile device."""
    return MOBILE_AGENT_RE.match(request.META['HTTP_USER_AGENT'])



#from stripe_python import get_clients

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
        'clients': jData,
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
   
    context = {
        'form': IntakeForm,
    }
        return render(request, 'ecommerce/index.html', context)

@csrf_exempt
def demo(request):
   
    context = {
        'form': IntakeForm,
    }
        return render(request, 'ecommerce/demo.html', context)

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

 name = request.POST.get("name", "")
 #now = datetime.datetime

# Format the datetime object as a string
 subject = datetime.datetime.now().strftime("%I:%M%p on %B %d, %Y")

 message = request.POST.get("message", "")
 phone = request.POST.get("phone", "")
 email = request.POST.get("email", "")

 Potential.objects.create(Company=name, Notes = subject + " " + message + " " + phone + " " + email)


       
        # In reality we'd use a form class
        # to get proper validation errors.
 return HttpResponseRedirect("/contact/thanks/")

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

class CheckoutSessionView(View):
    permission_classes = [HasAPIKey]
    def post(self, request, *args, **kwargs):
        permission_classes = [HasAPIKey]
        stripe.api_key = 'sk_test_51M1yvHABMyiljblNlxgjC76jKwkn5GCWjdBruPz2VWfESIgdBqaJvMqvwQ5F0H1Gt7zF2TnlYRWZNVEpKmcbcRNd00y0elqhRX'
        req_json = json.loads(request.body)
        #customer = stripe.Customer.create(name=request.user.username, email=request.user.username)
        customer = stripe.Customer.create(name='Cole', email='coleparsons22@gmail.com')
        #serializer = JobSerializer(data=request.data)
        #if serializer.is_valid():
            #product_id = request.data.get('id')
        product_id=json.loads(request.body)['items'][0]['id']#req_json["items"]["id"]   
        #product_id = self.request.GET.get('id')
        pp = pprint.PrettyPrinter(indent=4)
        pp.pprint(customer)
        #product_id = self.kwargs["id"]#112#serializer.data.get('id')#self.kwargs["pk"]
        #Business_Name = self.request.GET.get('BusinessName', None).replace("_", " ")
        product = Job.objects.get(id=product_id)
        fee = (product.Price + product.Tip)*0.029
        added = round((product.Price + product.Tip + fee), 2)
        #round(final_price,2)
        p = str(added*100)
        pp.pprint(p)
        total = p.replace(".0", "")
        t2=total[ 0 : 3 ]
        pp.pprint(t2)
        pp.pprint(total)
        YOUR_DOMAIN = "http://192.168.1.16:8000"
        stripe.checkout.Session.create(
                success_url=YOUR_DOMAIN + '/success?session_id={CHECKOUT_SESSION_ID}',
                cancel_url=YOUR_DOMAIN + '/cancelled/',
                payment_method_types=['card'],
                mode='payment',
                line_items=[
                    {
                    'price_data': {
                        'currency': 'usd',
                        'unit_amount': t2,
                        'product_data': {
                            'name': customer.name,
                            # 'images': ['https://i.imgur.com/EHyR2nP.png'],
                        },
                    },
                    'quantity': 1,
                },
            ],
            metadata={
                "product_id": product.id
            }

            )
        ephemeralKey = stripe.EphemeralKey.create(
        customer=customer['id'],
        stripe_version='2022-08-01',
        )    
        intent = stripe.PaymentIntent.create(
                amount=total,    #product.price,
                currency='usd',
                customer=customer['id'],
                automatic_payment_methods={
                    'enabled': True,
                },
                metadata={
                    "product_id": product.id
                }
            )
        return JsonResponse({'paymentIntent':intent.client_secret,
                 'ephemeralKey':ephemeralKey.secret,
                 'customer':customer.id,
                 'publishableKey':'sk_test_51M1yvHABMyiljblNlxgjC76jKwkn5GCWjdBruPz2VWfESIgdBqaJvMqvwQ5F0H1Gt7zF2TnlYRWZNVEpKmcbcRNd00y0elqhRX'}) #JsonResponse({'intentClientSecret': intent['client_secret']})

@csrf_exempt
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META['HTTP_STRIPE_SIGNATURE']
    event = None

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except ValueError as e:
        # Invalid payload
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        return HttpResponse(status=400)

    # Handle the checkout.session.completed event
    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']

        customer_email = session["customer_details"]["email"]
        product_id = session["metadata"]["product_id"]

        product = Job.objects.get(id=product_id)

        send_mail(
            subject="Here is your product",
            message=f"Thanks for your purchase. Here is the product you ordered. The URL is {product.url}",
            recipient_list=[customer_email],
            from_email="matt@test.com"
        )

        # TODO - decide whether you want to send the file or the URL
    
    elif event["type"] == "payment_intent.succeeded":
        intent = event['data']['object']

        stripe_customer_id = intent["customer"]
        stripe_customer = stripe.Customer.retrieve(stripe_customer_id)

        customer_email = stripe_customer['email']
        product_id = intent["metadata"]["product_id"]

        product = Job.objects.get(id=product_id)

        send_mail(
            subject="Here is your product",
            message=f"Thanks for your purchase. Here is the product you ordered. The URL is {product.url}",
            recipient_list=[customer_email],
            from_email="matt@test.com"
        )

    return HttpResponse(status=200)

@csrf_exempt
class StripeIntentView(View):
    @csrf_exempt
    def post(self, request, *args, **kwargs):
        try:
            req_json = json.loads(request.body)
            customer = stripe.Customer.create(email=req_json['email'])
            item_id = self.kwargs["pk"]
            product = Item.objects.get(Item_Number=item_id)
            
            intent = stripe.PaymentIntent.create(
                amount=Item.Retail_Price,
                currency='usd',
                customer=customer['id'],
                metadata={
                    "item_id": Item.id
                }
            )
            return JsonResponse({
                'clientSecret': intent['client_secret']
            })
        except Exception as e:
            return JsonResponse({ 'error': str(e) })        

permission_classes = csrf_exempt
@csrf_exempt
def checkout(item_id):
    permission_classes = csrf_exempt
    item = Item.objects.get(pk=item_id)
    domain_url = 'http://192.168.1.16:8080'
    #stripe.api_key = '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'

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
                    "name": item.Item_Number,
                    "quantity": 1,
                    "currency": 'usd',
                    "amount": int(float(item.Retail_Price) * 100),
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
            clients = stripe.Product.list(expand = ['data.default_price'])
            productdict = []
            for product in clients:
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
        local_clients = []
        for aJsonPath in get_product():  
            if 'featured.json' in aJsonPath:
                continue
            local_json = load_json_product(aJsonPath)
            local_clients.append(json.dumps( local_json, indent=4, separators=(',', ': ') ))


        context['productdict'] = json_data
        context['local_clients'] = local_clients

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
            clients = load_product_by_slug( slug )
            if clients:
                return redirect('/load-product')
        except:
            outputFile = f'clients/templates/clients/{slug}.json'
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
                outputFile = f'clients/templates/clients/featured.json'
            else:
                outputFile = f'clients/templates/clients/{slug}.json'

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
        outputFile = f'clients/templates/clients/{slug}.json'
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

def featured(request):
    return render(request, 'ecommerce/featured.html')

def items(request):
    items=Item.objects.all()
    context = {
        'featured': load_product_by_slug('featured'),
        'form': IntakeForm,
        'items': items,
    }
    return render(request, 'ecommerce/items.html', context)

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
