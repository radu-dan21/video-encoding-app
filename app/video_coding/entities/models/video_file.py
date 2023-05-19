from abc import abstractmethod

from django.conf import settings
from django.db import models
from django_jsonform.models.fields import JSONField

from video_coding.entities.models.base import BaseModel
from video_coding.utils.ffmpeg import FFMPEG, Decode
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

    def set_ffprobe_info(self):
        self.ffprobe_info = FFPROBE.call(self.file_path)
        self.save(update_fields=['ffprobe_info'])

    @abstractmethod
    def run_workflow(self):
        self.set_ffprobe_info()


class OriginalVideoFile(BaseVideoFile):
    def compute_metrics(self):
        ...

    def run_workflow(self):
        super().run_workflow()
        for evf in self.encoded_video_files.all():
            evf.run_workflow()
        self.compute_metrics()


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

    def encode(self):
        self.encoding_time = FFMPEG.call(
            ["-i", self.original_video_file.file_path]
            + self.video_encoding.ffmpeg_args
            + [self.decoded_video_file_path]
        )
        self.save(update_fields=['encoding_time'])

    def run_workflow(self):
        super().run_workflow()
        self.encode()
        self.decoded_video_file.run_workflow()


class DecodedVideoFile(BaseVideoFile):
    encoded_video_file = models.OneToOneField(
        EncodedVideoFile,
        on_delete=models.CASCADE,
        related_name="decoded_video_file",
    )

    decoding_time = models.FloatField(null=True)

    def decode(self):
        self.decoding_time = Decode.call(
            input_file_path=self.encoded_video_file.file_path,
            output_file_path=self.file_path,
        )
        self.save(update_fields=['decoding_time'])

    def run_workflow(self):
        super().run_workflow()
        self.decode()
