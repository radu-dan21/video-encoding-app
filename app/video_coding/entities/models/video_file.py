import logging

from abc import abstractmethod

from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _
from django_jsonform.models.fields import JSONField

from video_coding.entities.models.base import BaseModel
from video_coding.utils.ffmpeg import FFMPEG, Decode
from video_coding.utils.ffprobe import FFPROBE


logger = logging.getLogger(__name__)


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

    def set_ffprobe_info(self) -> None:
        self.ffprobe_info = FFPROBE.call(self.file_path)
        self.save(update_fields=["ffprobe_info"])

    @abstractmethod
    def run_workflow(self) -> None:
        logger.info(f"Starting workflow for {self}")
        logger.info(f"Setting ffprobe info for {self}")
        self.set_ffprobe_info()


class OriginalVideoFile(BaseVideoFile):
    class Status(models.TextChoices):
        READY = "R", _("Ready")
        ENCODING = "E", _("Encoding child videos")
        METRICS = "M", _("Computing metrics")
        DONE = "D", _("Done")
        FAILED = "F", _("Failed")

    status = models.CharField(
        max_length=1,
        choices=Status.choices,
        default=Status.READY,
    )

    error_message = models.CharField(
        max_length=1024,
        blank=True,
        default="",
    )

    def set_status(self, status: Status.choices, commit=True) -> None:
        self.status = status
        if commit:
            self.save(update_fields=["status"])

    def set_failed(self, error_message="") -> None:
        self.set_status(self.Status.FAILED)
        self.error_message = error_message
        self.save(update_fields=["status", "error_message"])

    def encode_video_files(self) -> None:
        logger.info(f"Encoding video files for {self}")
        self.set_status(self.Status.ENCODING)
        for evf in self.encoded_video_files.all():
            evf.run_workflow()

    def compute_metrics(self) -> None:
        logger.info(f"Computing metrics for {self}")
        self.set_status(self.Status.METRICS)
        ...

    def run_workflow(self) -> None:
        try:
            super().run_workflow()
            self.encode_video_files()
            self.compute_metrics()
            self.set_status(self.Status.DONE)
        except Exception as e:
            self.set_failed(str(e))
            raise e


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

    def encode(self) -> None:
        self.encoding_time = FFMPEG.call(
            ["-i", self.original_video_file.file_path]
            + self.video_encoding.ffmpeg_args
            + [self.decoded_video_file_path]
        )[0]
        self.save(update_fields=["encoding_time"])

    def run_workflow(self) -> None:
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

    def decode(self) -> None:
        self.decoding_time = Decode.call(
            input_file_path=self.encoded_video_file.file_path,
            output_file_path=self.file_path,
        )
        self.save(update_fields=["decoding_time"])

    def run_workflow(self) -> None:
        super().run_workflow()
        self.decode()
