from django.conf import settings
from django.db import models
from django_jsonform.models.fields import JSONField

from video_coding.entities.models.base import BaseModel
from video_coding.utils.ffprobe import FFPROBE


VIDEOS_PATH = settings.VIDEOS_PATH


class BaseVideoFile(BaseModel):
    file_path = models.CharField(
        blank=True,
        default="",
    )

    ffprobe_info = JSONField(
        schema=FFPROBE.SCHEMA,
        null=True,
        blank=True,
    )


class OriginalVideoFile(BaseVideoFile):
    ...


class EncodedVideoFile(BaseVideoFile):
    class Meta:
        unique_together = ("original_video_file", "video_encoding")

    original_video_file = models.ForeignKey(
        OriginalVideoFile,
        on_delete=models.CASCADE,
        related_name="encoded_video_files",
    )

    video_encoding = models.ForeignKey(
        "VideoEncoding",
        on_delete=models.CASCADE,
        related_name="encoded_video_files",
    )

    encoding_time = models.FloatField(null=True)


class DecodedVideoFile(BaseVideoFile):
    encoded_video_file = models.OneToOneField(
        EncodedVideoFile,
        on_delete=models.CASCADE,
        related_name="decoded_video_file",
    )

    decoding_time = models.FloatField(null=True)
