from django.db import models
from django_jsonform.models.fields import ArrayField

from video_coding.entities.models.base import BaseModel


class VideoEncoding(BaseModel):
    ffmpeg_args = ArrayField(
        models.CharField(max_length=BaseModel.MAX_CHAR_FIELD_LEN),
    )
