from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .auth_views import SetPasswordViewSet, SignupViewSet, LoginUserViewSet, UpdateUserViewSet, ResetPasswordView, SetPasswordViewSet, ChangePasswordViewSet, DeactivateUserViewSet, ProfileViewset, verify_email_for_signup, verify_reset_password, verify_deactivate_account, verify_email_for_update

urlpatterns = [
    path('login/', LoginUserViewSet.as_view(), name='login'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('signup/', SignupViewSet.as_view({'post': 'create'}), name='signup'),
    path('verify', verify_email_for_signup, name='verify_email'),
    path('account/update/<uuid:uuid>', UpdateUserViewSet.as_view({'put': 'update', 'patch': 'partial_update'}), name='account_update'),
    path('update/verify', verify_email_for_update, name='update_verify'),
    path('password/reset/', ResetPasswordView.as_view(), name='password_reset'),
    path('password/reset/verify', verify_reset_password, name='password_reset_verify'),
    path('password/set/', SetPasswordViewSet.as_view(), name='set_password'),
    path('password/change/', ChangePasswordViewSet.as_view(), name='password_change'),
    path('profile/', ProfileViewset.as_view(), name='profile'),
    path('account/deactivate/', DeactivateUserViewSet.as_view({'delete': 'destroy'}), name='account_deactivate'),
    path('deactivate/account/verify', verify_deactivate_account, name='verify_deactiavte_account')
]

# "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6MTc1NzE2MzYyOSwiaWF0IjoxNzU2NTU4ODI5LCJqdGkiOiIyN2Y1MGYzY2JmMmI0NDQ5YjI2ZTIzNzQ0ODJmNWZjOSIsImVtYWlsIjoiNTg3ZWY1MDItYTBjNC00MDYxLWFiYjMtNjZiMTA0ZDE3MDgwIn0.M_UsaVbd7BgzaUZL59IyO88rfAw6tUzXplb1lor47fg"
