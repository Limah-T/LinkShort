from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .auth_views import SignupViewSet, LoginUserViewSet, UpdateUserViewSet, DeactivateUserViewSet, verify_email_for_signup

urlpatterns = [
    path('login/', LoginUserViewSet.as_view(), name='login'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('signup/', SignupViewSet.as_view({'post': 'create'}), name='signup'),
    path('verify/', verify_email_for_signup, name='verify_email'),
    path('account/update/', UpdateUserViewSet.as_view({'put': 'update', 'patch': 'partial_update'}), name='account_update'),
    path('account/deactivate/', DeactivateUserViewSet.as_view({'delete': 'destroy'}), name='account_deactivate'),
]