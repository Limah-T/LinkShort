from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from .forms import ShortenForm, TitleForm
from django.views.generic.edit import FormView
from django.utils.crypto import get_random_string
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from dotenv import load_dotenv
from shortner.models import LinkShortner
from user.models import CustomUser
import os

load_dotenv()

def short(request):
    form = ShortenForm()
    title_form = TitleForm()
    all_links = LinkShortner.objects.all().order_by("-created_at")
    return render(request, "shortner/shortner.html", {'form':form, 'title_form': title_form, 'URLs': all_links})

class Shortner(FormView):
    form_class = ShortenForm
    template_name = "shortner/shortner.html"
    success_url = reverse_lazy("shortner:short")

    def post(self, request, *args, **kwargs):
        form = self.get_form(self.form_class)
        if form.is_valid():
            LONG_URL = form.cleaned_data.get("long_url")
            HOST = request.get_host()
            CODE = get_random_string(int(os.environ.get("CODE_LENGTH"))).lower()
            DOMAIN = os.environ.get("DOMAIN")
            short_url = f"{DOMAIN}{HOST}/{CODE}"
            user = CustomUser.objects.get(email="limahenterprises152@gmail.com")
            print(user)
            url_id = LinkShortner.objects.create(
                user_id = user,
                long_url = LONG_URL.strip(),
                short_url = short_url,
                code = CODE.strip(),
            )

            self.request.session['url_id'] = str(url_id.id)
            title_form = TitleForm()
            return render(request, "shortner/shortner.html", {'title_form': title_form, 'short_url': short_url})
        return super().post(request, *args, **kwargs)
    
class LinkTitle(FormView):
    form_class = TitleForm
    template_name = "shortner/shortner.html"
    success_url = reverse_lazy("shortner:short")

    def post(self, request, *args, **kwargs):
        url_id = request.session.get("url_id")
        try:
            url = LinkShortner.objects.get(id=url_id)
            print(url.short_url)
        except LinkShortner.DoesNotExist:
            messages.error(request, message="Invalid Request")
        except LinkShortner.MultipleObjectsReturned:
            messages.error(request, message="Invalid Request")
        except Exception as e:
            print(e)
            messages.error(request, message="Please try again later!")
        form = self.get_form(self.form_class)
        if form.is_valid():
            title = form.cleaned_data.get('title', None)
            if title:
                print("Yessss")
                url.title = title.strip().title()
            else:
                title = "Untitled"
            url.save()
            messages.success(request, message="Link has been saved successfully")
            
        return super().post(request, *args, **kwargs)

