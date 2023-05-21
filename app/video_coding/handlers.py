from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from video_coding.entities.models import BaseVideoFile


@receiver(post_save, sender=BaseVideoFile)
def base_video_file_post_save(sender, instance, created, raw, using, update_fields):
    if not created:
        return
    instance.create_folder_structure()


@receiver(post_delete, sender=BaseVideoFile)
def base_video_file_post_delete(sender, instance, using):
    instance.remove_folder_structure()
