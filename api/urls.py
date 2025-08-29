from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .auth_views import SetPasswordViewSet, SignupViewSet, LoginUserViewSet, UpdateUserViewSet, ResetPasswordView, SetPasswordViewSet, DeactivateUserViewSet, verify_email_for_signup, verify_reset_password

urlpatterns = [
    path('login/', LoginUserViewSet.as_view(), name='login'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('signup/', SignupViewSet.as_view({'post': 'create'}), name='signup'),
    path('verify/', verify_email_for_signup, name='verify_email'),
    path('account/update/', UpdateUserViewSet.as_view({'put': 'update', 'patch': 'partial_update'}), name='account_update'),
    path('password/reset/', ResetPasswordView.as_view(), name='password_reset'),
    path('password/reset/verify/', verify_reset_password, name='password_reset_verify'),
    path('password/set/', SetPasswordViewSet.as_view(), name='set_password'),
    path('account/deactivate/', DeactivateUserViewSet.as_view({'delete': 'destroy'}), name='account_deactivate'),
]

# eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6MTc1NzA4NTY3OCwiaWF0IjoxNzU2NDgwODc4LCJqdGkiOiI0NzEzMGZlMjk5Zjg0MDFlYTdlOTJlZTg5ZmM4ZTU2NSIsImVtYWlsIjoiNGY2MWFmYzctZGQyZi00NmJhLTgyY2MtZWU1NTAzNzI2ZTkyIn0.4Aj85NSELsDkDNJWdduRWobmd8deftwjzoj6stl3650