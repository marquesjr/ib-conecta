from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
from django.dispatch import receiver

from apps.accounts.models import Profile, Role

User = get_user_model()


@receiver(post_save, sender=User)
def ensure_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.get_or_create(user=instance, defaults={"role": Role.MEMBER})
    else:
        Profile.objects.get_or_create(user=instance)


@receiver(post_save, sender=Profile)
def sync_cms_access_on_profile_save(sender, instance, **kwargs):
    from apps.public.cms import sync_cms_access_for_user

    sync_cms_access_for_user(instance.user)
