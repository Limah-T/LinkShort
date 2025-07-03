from django.urls import path
from . import views

app_name = "shortner"

urlpatterns = [
    path("short/", views.short, name="short"),
    path("shorten/", views.Shortner.as_view(), name="shorten"),
    path("title/", views.LinkTitle.as_view(), name="title")
]