from .models import CustomUser, Link
from rest_framework import serializers
from .tasks import send_verification_email, encode_jwt

class CustomUserSerializer(serializers.Serializer):
    uuid = serializers.UUIDField(read_only=True)
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate_email(self, value):
        """ Validate the email address """
        if CustomUser.objects.filter(email=value.strip()).exists():
            raise serializers.ValidationError("Email is already in use.")
        return value.strip()
    
    def validate_password(self, value):
        """ Validate the password """
        if len(value) < 8:
            raise serializers.ValidationError("Password must be at least 8 characters long.")
        return value.strip()
    
    def create(self, validated_data):
        user = CustomUser(**validated_data)
        user.set_password(validated_data['password'])
        send_verification_email(
            to_email=user.email,
            subject="Verify your email",
            template_name="api/signup_verification.html",
            text_template_name="api/text_mails/signup_verification.txt"
        )
        user.save()
        return user

    