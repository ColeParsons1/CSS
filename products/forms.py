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

