from django.contrib.auth import authenticate
from rest_framework.response import Response
from rest_framework import status
from rest_framework import viewsets
from rest_framework import permissions
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.renderers import TemplateHTMLRenderer, JSONRenderer
from rest_framework.decorators import api_view, permission_classes, authentication_classes, renderer_classes
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .serializers import CustomUserSerializer, LoginToGetToken, ResetPasswordSerializer, SetPasswordSerializer
from .models import CustomUser
from .tasks import decode_jwt
from rest_framework_simplejwt.token_blacklist.models import OutstandingToken, BlacklistedToken

# Create account view
class SignupViewSet(viewsets.ModelViewSet):
    authentication_classes = []  # No authentication needed here
    permission_classes = [permissions.AllowAny]  # Anyone can access this view
    http_method_names = ['post']
    serializer_class = CustomUserSerializer
    
    def create(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"message": "Please check your email for verification"}, status=status.HTTP_200_OK)

# Verify email for signup
@api_view(['GET'])
@permission_classes([permissions.AllowAny]) # Anyone can access this view
@authentication_classes([]) # No authentication needed here
@renderer_classes([JSONRenderer, TemplateHTMLRenderer])
def verify_email_for_signup(request):
    token = request.GET.get("token") or request.query_params.get("token")
    if not token:
        return Response(data={"error": "Token is required"}, status=status.HTTP_400_BAD_REQUEST, template_name="api/invalid_token.html")
    
    payload = decode_jwt(token)
    if not payload:
        return Response(data={"error": "Invalid token"}, status=status.HTTP_400_BAD_REQUEST, template_name="api/invalid_token.html")
    
    email = payload.get("sub", None)
    if not email:
        return Response(data={"error": "Invalid token"}, status=status.HTTP_400_BAD_REQUEST, template_name="api/invalid_token.html")
    
    user = CustomUser.objects.filter(email=email).first()
    if not user:
        return Response(data={"error": "User not found"}, status=status.HTTP_404_NOT_FOUND, template_name="api/invalid_token.html")
    
    if user.verified:
        return Response(data={"message": "Email already verified"}, status=status.HTTP_400_BAD_REQUEST, template_name="api/invalid_token.html")
    
    user.verified = True
    user.save()
    return Response(data={"success": "Email verified successfully, login with your credentials to get started"}, status=status.HTTP_201_CREATED, template_name="api/email_verified.html")

# Login user
class LoginUserViewSet(TokenObtainPairView):
    authentication_classes = [] # No authentication needed here
    permission_classes = [permissions.AllowAny] # Anyone can access this view
    serializer_class = LoginToGetToken

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        user_data = serializer.validated_data
        return Response({
            "success": "Logged In",
            "uuid": user_data["user"]["uuid"],
            "access": user_data["access"],
            "refresh": user_data["refresh"]
        }, status=status.HTTP_200_OK)

# Update user
class UpdateUserViewSet(viewsets.ModelViewSet):
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ['patch', 'put']
    serializer_class = CustomUserSerializer

    def update(self, request, *args, **kwargs):
        print(request.user)
        serializer = self.serializer_class(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"message": "Please check your email for verification"}, status=status.HTTP_200_OK)

# Verify email for update
@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([permissions.IsAuthenticated])
@renderer_classes([JSONRenderer, TemplateHTMLRenderer])
def verify_email_for_update(request):
    user = request.user
    token = request.GET.get("token") or request.query_params.get("token")
    if not token:
        return Response(data={"error": "Token is required"}, status=status.HTTP_400_BAD_REQUEST, template_name="api/invalid_token.html")
    
    payload = decode_jwt(token)
    if not payload:
        return Response(data={"error": "Invalid token"}, status=status.HTTP_400_BAD_REQUEST, template_name="api/invalid_token.html")
    
    uuid = payload.get("user_id", None)
    # Check if it's the current user that request for an update 
    if not uuid or str(user.uuid) != uuid:
        return Response(data={"error": "Invalid token"}, status=status.HTTP_400_BAD_REQUEST, template_name="api/invalid_token.html")
    
    email = payload.get("sub", None)
    if not email:
        return Response(data={"error": "Invalid token"}, status=status.HTTP_400_BAD_REQUEST, template_name="api/invalid_token.html")
    
    if not user.is_active:
        return Response(data={"error": "User account is deactivated"}, status=status.HTTP_400_BAD_REQUEST, template_name="api/invalid_token.html")
    if not user.verified:
        return Response(data={"error": "User account is not verified"}, status=status.HTTP_400_BAD_REQUEST, template_name="api/invalid_token.html")
    
    user.email = email
    user.save()
    return Response(data={"success": "Email updated successfully"}, status=status.HTTP_202_ACCEPTED, template_name="api/email_verified.html")

# Reset password request
class ResetPasswordView(APIView):
    authentication_classes = []
    permission_classes = [permissions.AllowAny]
    serializer_class = ResetPasswordSerializer
    http_method_names = ['post']

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(data={"message": "Password reset link sent to email"}, status=status.HTTP_200_OK)

# Password reset verification
@api_view(['GET'])
@authentication_classes([]) # No authentication needed here
@permission_classes([permissions.AllowAny]) # Anyone can access this view
@renderer_classes([JSONRenderer, TemplateHTMLRenderer])
def verify_reset_password(request):
    token = request.GET.get("token") or request.query_params.get("token")
    if not token:
        return Response(data={"error": "Token is required"}, status=status.HTTP_400_BAD_REQUEST, template_name="api/invalid_token.html")
    payload = decode_jwt(token)
    if not payload:
        return Response(data={"error": "Invalid token"}, status=status.HTTP_400_BAD_REQUEST, template_name="api/invalid_token.html")
    email = payload.get("sub", None)
    if not email:
        return Response(data={"error": "Invalid token"}, status=status.HTTP_400_BAD_REQUEST, template_name="api/invalid_token.html")
    user = CustomUser.objects.filter(email=email).first()
    if not user:
        return Response(data={"error": "User not found"}, status=status.HTTP_404_NOT_FOUND, template_name="api/invalid_token.html")
    if not user.is_active:
        return Response(data={"error": "User account is deactivated"}, status=status.HTTP_400_BAD_REQUEST, template_name="api/invalid_token.html")
    if not user.verified:
        return Response(data={"error": "User account is not verified"}, status=status.HTTP_400_BAD_REQUEST, template_name="api/invalid_token.html")
    user.reset_password = True
    user.save()
    return Response(data={"success": "Verification successful"}, status=status.HTTP_200_OK, template_name="api/email_verified.html")

# Set password
class SetPasswordViewSet(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ['post']
    serializer_class = SetPasswordSerializer

    def post(self, request, *args, **kwargs):
        user = request.user
        if not user.is_active:
            return Response(data={"error": "User account is deactivated"}, status=status.HTTP_400_BAD_REQUEST)
        if not user.verified:
            return Response(data={"error": "User account is not verified"}, status=status.HTTP_400_BAD_REQUEST)
        if not user.reset_password:
            return Response(data={"error": "Password reset not verified, request a new password reset"}, status=status.HTTP_400_BAD_REQUEST)
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        new_password = serializer.validated_data.get("new_password")
        old_password = user.password
        if old_password == new_password:
            return Response(data={"error": "New password cannot be the same as the old password"}, status=status.HTTP_400_BAD_REQUEST)
        user.set_password(new_password)
        user.reset_password = False
        user.save()
        return Response(data={"success": "Password has been reset successfully"}, status=status.HTTP_200_OK)    

# Deactivate user
class DeactivateUserViewSet(viewsets.ViewSet): # Viewset - since no queryset needed
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ['delete']
    
    def destroy(self, request, *args, **kwargs):
        user = request.user
        user.is_active = False
        user.save(update_fields=["is_active"])
        return Response(data={"success": "User's account has been deactivated successfully"}, status=status.HTTP_204_NO_CONTENT)
