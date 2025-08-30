from .models import CustomUser, Link
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .tasks import send_verification_email, signup_token, update_token, reset_password_token

class CustomUserSerializer(serializers.Serializer):
    uuid = serializers.UUIDField(read_only=True)
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate_email(self, value):
        """ Validate the email address """
        if not value:
            raise serializers.ValidationError("Email is required.")
        value = value.strip().lower()
        return value

    def validate_password(self, value):
        """ Validate the password """
        if len(value) < 8:
            raise serializers.ValidationError("Password must be at least 8 characters long.")
        return value.strip()
    
    def create(self, validated_data):
        email = validated_data.get("email")
        if CustomUser.objects.filter(email=email.strip().lower()).exists():
            raise serializers.ValidationError("Email is already in use.")
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

class LoginToGetToken(TokenObtainPairSerializer):
    email = serializers.EmailField(write_only=True)
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):

        attrs['email'] = attrs['email'].strip().lower()
        data = super().validate(attrs)

        user = self.user
        if not user:
            raise serializers.ValidationError("Invalid email or password.")
        if not user.verified:
            raise serializers.ValidationError("User account is not verified.")
        if not user.is_active:
            raise serializers.ValidationError("User account is deactivated.")
        data.update({
            "user": {
                "uuid": str(user.uuid),
            }
        })
        return data

class ResetPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        if not value:
            raise serializers.ValidationError("Email is required.")
        email = value.strip().lower()
        try:
            user = CustomUser.objects.get(email=email)
        except CustomUser.DoesNotExist:
            raise serializers.ValidationError("User with this email does not exist.")
        except Exception as e:
            raise serializers.ValidationError("An error occurred while processing your request.")
        if not user.verified:
            raise serializers.ValidationError("User account is not verified.")
        
        verification_url = reset_password_token(email=user.email, uuid=user.uuid)
        print(verification_url)
        send_verification_email(
            verification_url=verification_url,
            to_email=user.email,
            subject="Reset your password",
            template_name="api/reset_password.html",
            text_template_name="api/text_mails/reset_password.txt"
        )
        return email
    
class SetPasswordSerializer(serializers.Serializer):
    new_password = serializers.CharField(write_only=True)

    def validate_new_password(self, value):
        if len(value) < 8:
            raise serializers.ValidationError("Password must be at least 8 characters long.")
        return value.strip()

class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        password1 = attrs.get("old_password", None)
        password2 = attrs.get("new_password", None)
        if not password1 or not password2:
            raise serializers.ValidationError("Both old_password and new_password fields are required")
        if len(password1) < 8 or len(password2) < 8:
            raise serializers.ValidationError("Password must be at least 8 characters long.")
        if password1.strip() == password2.strip():
            raise serializers.ValidationError("Old and new password cannot be the same.")
        return attrs