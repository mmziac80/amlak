from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model

User = get_user_model()

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        # ایجاد پروفایل کاربری پس از ثبت‌نام
        from users.models import Profile
        Profile.objects.create(user=instance)
