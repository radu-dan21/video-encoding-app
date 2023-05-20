from django.db import models
from django_jsonform.models.fields import ArrayField

from video_coding.entities.models.base import BaseModel


class VideoEncoding(BaseModel):
    ffmpeg_args = ArrayField(
        models.CharField(max_length=BaseModel.MAX_CHAR_FIELD_LEN),
    )

    # if blank, the extension of the original video file will be used
    video_extension = models.CharField(
        max_length=5,
        default="",
        blank=True,
    )
