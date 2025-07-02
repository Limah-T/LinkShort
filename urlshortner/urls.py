from django.contrib import admin
from django.urls import path, include
from user import views
urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home),
    path("user/", include("user.urls")),
    path('accounts/', include('allauth.urls')),
    
]
