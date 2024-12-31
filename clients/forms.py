from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.forms import HiddenInput


class IntakeForm(forms.ModelForm):
    name = forms.CharField(label='Full Name', max_length=100, required=False)
    phone = forms.CharField(label='Phone', max_length=100, required=False)
    email = forms.EmailField(label='Email',max_length=54, required=False, help_text='')

    class Meta:
        model = User
        fields = ('name', 'phone', 'email',)

class sign(UserCreationForm):
    email = forms.EmailField(label='Email',max_length=54, required=True, help_text='')
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Password confirmation', widget=forms.PasswordInput)
    birth_date = forms.DateField(label="When's your birthday?", widget=forms.SelectDateWidget())
    location = forms.CharField(label='Location',max_length=30, required=False)

    class Meta:
        model = User
        fields = ('username', 'birth_date', 'location',)        

