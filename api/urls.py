from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .auth_views import SetPasswordViewSet, SignupViewSet, LoginUserViewSet, UpdateUserViewSet, ResetPasswordView, SetPasswordViewSet, ChangePasswordViewSet, DeactivateUserViewSet, ProfileViewset, ViewAllUsersViewset, LogoutViewset, verify_email_for_signup, verify_reset_password, verify_deactivate_account, verify_email_for_update

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
    path('users/', ViewAllUsersViewset.as_view({'get': 'list'}), name='users'),
    path('logout/', LogoutViewset.as_view(), name='logout'),
    path('account/deactivate/', DeactivateUserViewSet.as_view({'delete': 'destroy'}), name='account_deactivate'),
    path('deactivate/account/verify', verify_deactivate_account, name='verify_deactiavte_account')
]
    