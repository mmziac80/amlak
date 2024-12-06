from django.db.models.signals import post_save
from django.dispatch import receiver
from properties.models import Property
from django.core.cache import cache

@receiver(post_save, sender=Property)
def clear_cache(sender, instance, **kwargs):
    # پاک کردن کش پس از تغییر در املاک
    cache.delete('property_list')
