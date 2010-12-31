from django import forms

class APIKeyForm(forms.Form):
    userid = forms.CharField(max_length=8)
    apikey = forms.CharField(max_length=64)
