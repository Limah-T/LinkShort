from rest_framework.response import Response
from rest_framework import status
from rest_framework import viewsets
from rest_framework import permissions
from rest_framework import authentication
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from .serializers import CustomUserSerializer
from .models import CustomUser
from .tasks import decode_jwt

class CustomUserViewSet(viewsets.ModelViewSet):
    authentication_classes = [authentication.SessionAuthentication]
    permission_classes = [permissions.AllowAny]
    http_method_names = ['post']
    serializer_class = CustomUserSerializer

    def get_queryset(self):
        return CustomUser.objects.all()
    
    def create(self, request, *args, **kwargs):
        CustomUser.objects.all().delete()
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        print(serializer.validated_data)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

@api_view(['GET'])
@permission_classes([permissions.AllowAny])
@authentication_classes([authentication.SessionAuthentication])
def verify_email(request):
    token = request.query_params.get("token") or request.GET.get("token")
    if not token:
        return Response({"error": "Token is required"}, status=status.HTTP_400_BAD_REQUEST)
    payload = decode_jwt(token)
    if not payload:
        return Response({"error": "Invalid token"}, status=status.HTTP_400_BAD_REQUEST)
    email = payload.get("aud")
    if not email:
        return Response({"error": "Invalid token"}, status=status.HTTP_400_BAD_REQUEST)
    user = CustomUser.objects.filter(email=email).first()
    if not user:
        return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

    user.verified = True
    user.save()
    return Response({"success": "Email verified successfully"}, status=status.HTTP_200_OK)
