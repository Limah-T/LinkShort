from django import forms
from user.models import CustomUser

class ShortenForm(forms.Form):
    long_url = forms.URLField(max_length=500, required=True, label="...",
                              widget=forms.TextInput(attrs={'class': 'form-control'})
                              )

class TitleForm(forms.Form):
    title = forms.CharField(max_length=100, required=False, 
                            widget=forms.TextInput(attrs=
                                                   {'class': 'form-control',
                                                    'placeholder': 'e.g My Youtube channel'
                                                }))
