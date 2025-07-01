from django.contrib.auth.forms import UserCreationForm
from django import forms
from .models import CustomUser

class SignupForm(UserCreationForm):
    first_name = forms.CharField(max_length=50, min_length=3, required=True, 
                                 widget=forms.TextInput(attrs={'class': 'form-control'}))
    last_name = forms.CharField(max_length=50, min_length=3, required=True,
                                widget=forms.TextInput(attrs={'class': 'form-control'}))
    email = forms.EmailField(max_length=50, required=True,
                             widget=forms.TextInput(attrs={'class': 'form-control'}))
    password1 = forms.CharField(label="Password", required=True,
                                widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    password2 = None

    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'email']
    
    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get('email')
        first_name = cleaned_data.get('first_name')
        last_name = cleaned_data.get('last_name')
        if email:
            cleaned_data['email'] = email.strip().lower()
        if first_name:
            cleaned_data['first_name'] = first_name.strip().capitalize()
        if last_name:
            cleaned_data['last_name'] = last_name.strip().capitalize()
        return cleaned_data

class LoginForm(forms.Form):
    email = forms.EmailField(max_length=50, required=True,
                             widget=forms.TextInput(attrs={'class': 'form-control'}))
    password = forms.CharField(label="Password", required=True,
                                widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    
    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get('email')
        password = cleaned_data.get('password')

        if email:
            cleaned_data['email'] = email.strip().lower()
        if password:
            cleaned_data['password'] = password.strip()
        return cleaned_data