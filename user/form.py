from django.contrib.auth.forms import UserCreationForm
from django import forms
from .models import CustomUser

class SignupForm(UserCreationForm):
    username = forms.CharField(max_length=50, min_length=3, required=True,
                                widget=forms.TextInput(attrs={'class': 'form-control'}))
    email = forms.EmailField(max_length=50, required=True,
                             widget=forms.TextInput(attrs={'class': 'form-control'}))
    password1 = forms.CharField(label="Password", required=True,
                                widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    password2 = forms.CharField(label="Confirm Password", required=True,
                                widget=forms.PasswordInput(attrs={'class': 'form-control'}))

    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'password1', 'password2']
    
    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get('email')
        username = cleaned_data.get('username')
        if email:
            cleaned_data['email'] = email.strip().lower()
        if username:
            cleaned_data['username'] = username.strip().capitalize()
    
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