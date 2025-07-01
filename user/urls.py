from django.urls import path, include
from . import views

app_name = "user"
urlpatterns = [
    path("home/", views.home, name="home"),
    path("login/", views.LoginView.as_view(), name="login"),
    path("signup/", views.SignUpView.as_view(), name="signup"),
    path("verify-email/", views.VerifyEmail, name="verify-email"),
    path("logout/", views.logoutview, name="logout")
]
