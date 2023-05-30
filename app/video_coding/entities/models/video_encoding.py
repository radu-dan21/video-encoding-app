from django.db import models
from django_jsonform.models.fields import ArrayField

from video_coding.entities.models.base import BaseModel
from video_coding.entities.models.choices import VALID_VIDEO_FILE_CHOICES_LIST


class VideoEncoding(BaseModel):
    ffmpeg_args = ArrayField(
        models.CharField(max_length=BaseModel.MAX_CHAR_FIELD_LEN),
    )

    # if blank, the extension of the original video file will be used
    video_extension = models.CharField(
        blank=True,
        choices=VALID_VIDEO_FILE_CHOICES_LIST,
        default="",
        help_text=(
            "If blank, the original video's extension "
            "will be used for the encoded videos"
        ),
        max_length=5,
    )
