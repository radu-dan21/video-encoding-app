import logging
import os
import shutil

from abc import abstractmethod
from fractions import Fraction

from django.conf import settings
from django.core.validators import RegexValidator
from django.db import models
from django.utils.translation import gettext_lazy as _
from django_jsonform.models.fields import JSONField
from hurry.filesize import si, size

from video_coding.entities.models.base import BaseModel
from video_coding.entities.utils.decorators import ignore_errors
from video_coding.handlers import vf_post_delete_hook, vf_post_save_hook
from video_coding.utils import FFMPEG, FFPROBE, Decode


logger = logging.getLogger(__name__)


VIDEOS_PATH = settings.VIDEOS_PATH


class BaseVideoFile(BaseModel):
    class Meta:
        abstract = True

    @classmethod
    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        models.signals.post_save.connect(vf_post_save_hook, sender=cls)
        models.signals.post_delete.connect(vf_post_delete_hook, sender=cls)

    ffprobe_info = JSONField(
        blank=True,
        null=True,
        schema=FFPROBE.SCHEMA,
    )

    file_name = models.CharField(
        blank=True,
        default="",
        validators=[RegexValidator(regex=r"^(.+)\.(.){1,5}")],
    )

    @property
    @abstractmethod
    def parent_dir(self):
        ...

    @abstractmethod
    def run_workflow(self) -> None:
        logger.info(f"Starting workflow for {self}")
        logger.info(f"Setting ffprobe info for {self}")
        self.set_ffprobe_info()

    @property
    def extension(self) -> str:
        rightmost_dot_idx: int = self.file_name.rfind(".")
        return self.file_name[rightmost_dot_idx + 1 :]

    @property
    def file_path(self) -> str:
        return os.path.join(self.parent_dir, self.file_name)

    @property
    @ignore_errors([KeyError, TypeError])
    def bitrate(self) -> float | None:
        bps: int = int(self.ffprobe_info["format"]["bit_rate"])
        return round(bps / 10**6, 2)  # Mbps rounded to 2 decimals

    @property
    @ignore_errors([KeyError, TypeError])
    def duration(self) -> float | None:
        return round(float(self.ffprobe_info["format"]["duration"]), 2)

    @property
    @ignore_errors([KeyError, TypeError])
    def size(self) -> str | None:
        return size(int(self.ffprobe_info["format"]["size"]), system=si)

    @property
    @ignore_errors([KeyError, TypeError])
    def codec(self) -> str | None:
        return self.ffprobe_info["streams"][0]["codec_name"]

    @property
    @ignore_errors([KeyError, TypeError])
    def fps(self) -> float | None:
        avg_frame_rate = float(
            Fraction(self.ffprobe_info["streams"][0]["avg_frame_rate"])
        )
        return round(avg_frame_rate, 2)

    @property
    @ignore_errors([KeyError, TypeError])
    def resolution(self) -> str | None:
        return " x ".join(
            [str(self.ffprobe_info["streams"][0][k]) for k in ("width", "height")]
        )

    def set_ffprobe_info(self) -> None:
        self.ffprobe_info = FFPROBE.call(self.file_path)
        self.save(update_fields=["ffprobe_info"])

    def create_folder_structure(self) -> None:
        if not os.path.exists(self.parent_dir):
            os.makedirs(self.parent_dir)

    def remove_folder_structure(self) -> None:
        shutil.rmtree(self.parent_dir, ignore_errors=True)


class OriginalVideoFile(BaseVideoFile):
    class Status(models.TextChoices):
        READY = "R", _("Ready")
        ENCODING = "E", _("Encoding child videos")
        METRICS = "M", _("Computing metrics")
        DONE = "D", _("Done")
        FAILED = "F", _("Failed")

    status = models.CharField(
        choices=Status.choices,
        default=Status.READY,
        max_length=1,
    )

    error_message = models.CharField(
        max_length=1024,
        blank=True,
        default="",
    )

    @property
    def parent_dir(self) -> str:
        return os.path.join(VIDEOS_PATH, f"{self.id}/")

    def set_status(self, status: Status.choices, commit=True) -> None:
        self.status = status
        if commit:
            self.save(update_fields=["status"])

    def set_failed(self, error_message="") -> None:
        self.set_status(self.Status.FAILED)
        self.error_message = error_message
        self.save(update_fields=["status", "error_message"])

    def run_workflow(self) -> None:
        try:
            super().run_workflow()
            self.encode_video_files()
            self.compute_metrics()
            self.set_status(self.Status.DONE)
        except Exception as e:
            self.set_failed(str(e))
            raise e

    def encode_video_files(self) -> None:
        logger.info(f"Encoding video files for {self}")
        self.set_status(self.Status.ENCODING)
        for evf in self.encoded_video_files.all():
            evf.run_workflow()

    def compute_metrics(self) -> None:
        logger.info(f"Computing metrics for {self}")
        self.set_status(self.Status.METRICS)
        filter_results_fields: list[str] = [
            "info_filter_results",
            "comparison_filter_results",
        ]
        for filter_result_field in filter_results_fields:
            for f in getattr(self, filter_result_field).all():
                f.compute()


class EncodedVideoFile(BaseVideoFile):
    REL_PATH_TO_OVF: str = "encoded/"

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

    @property
    def parent_dir(self) -> str:
        return os.path.join(self.original_video_file.parent_dir, self.REL_PATH_TO_OVF)

    @property
    def comparison_filters(self) -> list:
        if not (dvf := self.decoded_video_file):
            return []
        return list(dvf.filter_results.all())

    def run_workflow(self) -> None:
        self.encode()
        super().run_workflow()
        self.decoded_video_file.run_workflow()

    def encode(self) -> None:
        self.encoding_time = FFMPEG.call(
            ["-y", "-i", f'"{self.original_video_file.file_path}"']
            + self.video_encoding.ffmpeg_args
            + [self.file_path]
        )[0]
        self.encoding_time = round(self.encoding_time, 5)
        self.save(update_fields=["encoding_time"])


class DecodedVideoFile(BaseVideoFile):
    REL_PATH_TO_OVF: str = "decoded/"

    encoded_video_file = models.OneToOneField(
        EncodedVideoFile,
        on_delete=models.CASCADE,
        related_name="decoded_video_file",
    )

    decoding_time = models.FloatField(null=True)

    @property
    def parent_dir(self):
        return os.path.join(self.original_video_file.parent_dir, self.REL_PATH_TO_OVF)

    @property
    def original_video_file(self) -> OriginalVideoFile:
        return self.encoded_video_file.original_video_file

    def run_workflow(self) -> None:
        self.decode()
        super().run_workflow()

    def decode(self) -> None:
        self.decoding_time = Decode.call(
            input_file_path=self.encoded_video_file.file_path,
            output_file_path=self.file_path,
        )
        self.save(update_fields=["decoding_time"])
