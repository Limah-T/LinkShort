from django.shortcuts import render, redirect
from django.urls import reverse_lazy, reverse
from django.views.generic.edit import FormView
from django.contrib import messages
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from .models import CustomUser
from shortner.models import LinkShortner
from shortner.forms import TitleForm, ShortenForm
from .message import send_token_for_email_verification, decode_token, verify_email_from_kickbox
from django.http import HttpResponse
from dotenv import load_dotenv
import os

load_dotenv(override=True)

from . import form

def home(request):
    return render(request, "account/home.html")

class SignUpView(FormView):
    form_class = form.SignupForm
    template_name = "account/signup.html"
    success_url = "user:home"

    def dispatch(self, request, *args, **kwargs):
        # CustomUser.objects.all().delete()
        current_user = request.user
        if current_user.is_authenticated:
            return redirect("user:home")
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        form = self.get_form(self.form_class)
        if form.is_valid():
            email = form.cleaned_data.get('email')
            # valid_email = verify_email_from_kickbox(email)
            # if valid_email.get("result") != "deliverable":
            #     messages.error(request, message="Sorry, we couldn't verify your email address, make sure you input the correct email address.")
            #     return redirect(reverse_lazy("user:signup"))
            form.save()
            if send_token_for_email_verification(user=email):
                pass
            else:
                try:
                    user_exist = CustomUser.objects.get(email=email)
                    user_exist.delete()
                except Exception as e:
                    print(e)
                    messages.error(request, message="Sorry, we couldn't send for verification due to network issue, please try again later!")
                    return redirect(reverse_lazy("user:signup"))
            return render(request, 'account/email_alert.html', {'email':email})
        return super().post(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['LINK'] = os.environ.get('LINK')
        return context
    
def VerifyEmail(request):
    token = request.GET.get('token')
    decoded_token = decode_token(token)
    if not decoded_token:
        return render(request, "account/failed_verification.html")
    email = decoded_token.get('sub')
    print(email)
    try:
        user = CustomUser.objects.get(email=email)
    except CustomUser.DoesNotExist:
        return render(request, "account/failed_verification.html")
    except CustomUser.MultipleObjectsReturned:
        return render(request, "account/failed_verification.html")
    except Exception as e:
        return render(request, "account/failed_verification.html")
    if user.email_verified or user.token_valid:
        return render(request, "account/failed_verification.html")
    user.email_verified = True
    user.token_valid = True
    user.save()
    user.backend = 'django.contrib.auth.backends.ModelBackend'
    login(request, user=user)
    messages.success(request, message="Successfully created an account 👏")
    return redirect("user:home")


class LoginView(FormView):
    form_class = form.LoginForm
    template_name = "account/login.html"
    success_url = reverse_lazy("user:home")

    def dispatch(self, request, *args, **kwargs):
        current_user = request.user
        if current_user.is_authenticated:
            return redirect("user:home")
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        form = self.get_form(self.form_class)
        if form.is_valid():
            email = form.cleaned_data.get('email')
            password = form.cleaned_data.get('password')
            print(email, password)
            try:
                usr = CustomUser.objects.get(email=email)
            except Exception as e:
                print(e)
                return HttpResponse("Wrong credentials")
            user = authenticate(request, username=usr.username, password=password)
            if user: 
                print(user)
                user.backend = 'django.contrib.auth.backends.ModelBackend'
                login(request, user=user)
                messages.success(request, message="Successfully Logged In")
                form = ShortenForm()
                title_form = TitleForm()
                all_links = LinkShortner.objects.all().order_by("-created_at")
                return render(request, "shortner/shortner.html", {'form':form, 'title_form': title_form, 'URLs': all_links})
            else:
                print(user)
                messages.error(request, message="Incorrect email or password")
                return render(request, "account/login.html", {'form': self.form_class})
        return super().post(request, *args, **kwargs)

@login_required(redirect_field_name="user:login")    
def logoutview(request):
    logout(request)
    messages.success(request, message="You are Logged out, log in to continue")
    return redirect(reverse("user:login"))
