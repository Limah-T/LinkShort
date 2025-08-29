from .models import CustomUser, Link
from rest_framework import serializers
from .tasks import send_verification_email, signup_token, update_token

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
        user.save()
        verification_url = signup_token(user.email, user.uuid)
        send_verification_email(
            verification_url=verification_url,
            to_email=user.email,
            subject="Verify your email",
            template_name="api/signup_verification.html",
            text_template_name="api/text_mails/signup_verification.txt"
        )
        return user
    
    def update(self, instance, validated_data):
        email = validated_data.get("email", None)
        if not email:
            raise serializers.ValidationError("Email is required")
        email = email.strip().lower()
        # Check if the user entered the same email
        if instance.email == email:
            raise serializers.ValidationError("New email cannot be the same as the current email.")
        # Check if the email has not been used by another user
        if CustomUser.objects.filter(email=email).exclude(uuid=instance.uuid).exists():
            raise serializers.ValidationError("Email is already in use.")
        verification_url = update_token(email, instance.uuid)
        send_verification_email(
            verification_url=verification_url,
            to_email=email,
            subject="Update your email by verifying",
            template_name="api/update_email.html",
            text_template_name="api/text_mails/update_email.txt"
        )
        return instance

    