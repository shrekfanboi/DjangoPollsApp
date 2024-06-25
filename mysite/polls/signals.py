from django.db.models.signals import post_delete, pre_save
from django.dispatch import receiver
from polls.models import User
import os

@receiver(pre_save, sender=User)
def delete_media_file_on_change(sender, instance, **kwargs):
    if instance.pk:
        try:
            old_file = User.objects.get(pk=instance.pk).avatar
        except User.DoesNotExist:
            return False
        new_file = instance.avatar
        if old_file and old_file.path != 'polls/default-avatar.png' and old_file != new_file:
            try:
                os.remove(old_file.path)
            except FileNotFoundError:
                print(f"Could not locate {old_file.path}")



@receiver(post_delete, sender=User)
def delete_media_file_on_delete(sender, instance, **kwargs):
    if instance.avatar and instance.avatar != 'polls/default-avatar.png':
        try:
            os.remove(instance.avatar.path)
        except FileNotFoundError:
            print(f"Could not locate {instance.avatar.path}")