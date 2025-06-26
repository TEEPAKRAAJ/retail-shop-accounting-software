from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from django.utils.crypto import get_random_string
from .models import Shop

def generate_unique_id():
    return get_random_string(length=10, allowed_chars='abcdefghijklmnopqrstuvwxyz0123456789')

@receiver(post_save, sender=User)
def create_user_shop(sender, instance, created, **kwargs):
    if created:
        unique_id = generate_unique_id()
        while Shop.objects.filter(unique_id=unique_id).exists():
            unique_id = generate_unique_id()
        Shop.objects.create(
            owner=instance,
            shop_name=f"{instance.username}'s Shop",
            unique_id=unique_id
        )
