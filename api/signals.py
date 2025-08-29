from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken, OutstandingToken
from django.dispatch import receiver
from django.db.models.signals import pre_delete, pre_save
from .models import CustomUser

@receiver(signal=pre_delete, sender=OutstandingToken)
def delete_blacklisted_tokens(sender, instance, **kwargs):
    # Delete all blacklisted tokens associated with the user
    BlacklistedToken.objects.filter(token__user=instance).delete()
    # Delete all outstanding tokens associated with the user
    OutstandingToken.objects.filter(user=instance.user).delete()

@receiver(signal=pre_save, sender=OutstandingToken)
def blacklist_token_for_password_reset(sender, instance, **kwargs):
    """
    When a user changes their password, blacklist all their existing tokens.
    """
    if not instance.uuid:
        # New user, no password change
        return
    try:
        old_password = CustomUser.objects.get(uuid=instance.uuid).password
    except CustomUser.DoesNotExist:
        return
    new_password = instance.password
    # If password is different, blacklist all tokens
    if old_password != new_password:
        tokens = OutstandingToken.objects.filter(user=instance)
        for token in tokens:
            BlacklistedToken.objects.get_or_create(token=token)
   