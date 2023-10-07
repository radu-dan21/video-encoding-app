from django.db import models
from django_jsonform.models.fields import ArrayField

from video_coding.entities.models.base import BaseModel
from video_coding.entities.models.choices import VALID_VIDEO_FILE_CHOICES_LIST


class Codec(BaseModel):
    """
    Represents a software encoder
    """

    ffmpeg_args = ArrayField(
        models.CharField(max_length=BaseModel.MAX_CHAR_FIELD_LEN),
    )


class VideoEncoding(BaseModel):
    """
    Represents a specific setting of a software encoder
    Used for encoding original video files
    """

    codec = models.ForeignKey(
        Codec,
        on_delete=models.CASCADE,
        related_name="settings",
    )

    extra_ffmpeg_args = ArrayField(
        models.CharField(max_length=BaseModel.MAX_CHAR_FIELD_LEN),
    )

    @property
    def ffmpeg_args(self) -> list[str]:
        return self.codec.ffmpeg_args + self.extra_ffmpeg_args

    # The extension that the encoded video file will have
    # If blank, the extension of the original video file will be used
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
