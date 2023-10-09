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
from video_coding.entities.models.bd_metric import BDMetric
from video_coding.entities.models.graph import EncodingTimeGraph, MetricGraph
from video_coding.entities.models.utils import MetricsData
from video_coding.entities.utils.decorators import ignore_errors
from video_coding.handlers import vf_post_delete_hook, vf_post_save_hook
from video_coding.tasks import remove_file_tree
from video_coding.utils import FFMPEG, FFPROBE, Decode


logger = logging.getLogger(__name__)


PROCESSED_VIDEOS_PATH = settings.PROCESSED_VIDEOS_PATH


class BaseVideoFile(BaseModel):
    """
    Abstract base class that defines the common behavior of
    all types of video files used throughout the project
    """

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
        help_text="Video metadata extracted with ffprobe.",
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
        """
        Method that starts the processing workflow for a video file
        Overriden in base classes for specific custom behaviour
        """
        logger.info(f"Starting workflow for {self}")
        if not self.ffprobe_info:
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
        return round(bps / 10**3, 2)  # Kbps rounded to 2 decimals

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
        remove_file_tree.delay(self.parent_dir)


class OriginalVideoFile(BaseVideoFile):
    """
    Represents the video file that a user wants to process
    """

    class Status(models.TextChoices):
        COPYING = "C", _("Copying video file")
        READY = "R", _("Ready")
        INFO_METRICS = "I", _("Computing original video metrics")
        ENCODING = "E", _("Encoding child videos")
        COMPARISON_METRICS = "M", _("Computing encoded video(s) metrics")
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
        return os.path.join(PROCESSED_VIDEOS_PATH, f"{self.id}/")

    @property
    def is_in_progress(self) -> bool:
        return self.status not in (
            self.Status.DONE,
            self.Status.FAILED,
        )

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
            self.compute_information_metrics()
            self.encode_video_files()
            self.compute_graphs_and_bd_metrics()
            self.set_status(self.Status.DONE)
        except Exception as e:
            self.set_failed(str(e))
            raise e

    def encode_video_files(self) -> None:
        """
        Responsible for starting the encoding process
        for each associated EncodedVideoFile
        """
        logger.info(f"Encoding video files for {self}")
        self.set_status(self.Status.ENCODING)
        for evf in self.encoded_video_files.all():
            evf.run_workflow()

    def compute_information_metrics(self) -> None:
        """
        Responsible for starting the computation process
        for each associated InformationFilterResult
        """
        logger.info(f"Computing information metrics for {self}")
        ifrs = self.info_filter_results.filter(output="")
        if ifrs:
            self.set_status(self.Status.INFO_METRICS)
            for ifr in ifrs:
                ifr.compute()

    def compute_graphs_and_bd_metrics(self) -> None:
        """
        Responsible for creating associated
        graphs and Bjøntegaard-Delta metrics
        """
        self.set_status(self.Status.COMPARISON_METRICS)
        md = MetricsData(self.id)
        self.compute_graphs(md)
        self.compute_bd_metrics(md)

    def compute_graphs(self, metrics_data: MetricsData) -> None:
        from video_coding.entities.models.filter import ComparisonFilter
        from video_coding.entities.models.graph import BaseGraph

        BaseGraph.objects.filter(original_video_file=self).delete()

        enc_time_graph_file_path = os.path.join(self.parent_dir, "enc_time.html")
        EncodingTimeGraph.objects.create(
            original_video_file=self,
            name=f"OVF {self.id} - encoding time",
            file_path=enc_time_graph_file_path,
        ).create_graph_file(metrics_data)

        for mn in metrics_data.get_metric_column_names():
            metric_graph_file_path = os.path.join(
                self.parent_dir,
                f"{mn.replace(' ', '_')}.html",
            )
            MetricGraph.objects.create(
                original_video_file=self,
                name=f"OVF {self.id} - {mn}",
                comparison_filter=ComparisonFilter.objects.get(name=mn),
                file_path=metric_graph_file_path,
            ).create_graph_file(metrics_data)

    def compute_bd_metrics(self, metrics_data: MetricsData) -> None:
        BDMetric.objects.filter(original_video_file=self).delete()
        BDMetric.compute(self, metrics_data)

    def handle_file_copy(self, source_path: str) -> None:
        """
        Handles copying the associated video file to its correct location
        Used when the user re-uses an existing video file and does not upload a new one
        :param source_path: Path to the existing video file
        """
        logger.info(f"Copying video from <{source_path}> to {self.parent_dir}!")
        self.set_status(self.Status.COPYING)
        try:
            shutil.copy2(source_path, self.parent_dir)
        except Exception as e:
            self.set_failed(str(e))
            raise e


class EncodedVideoFile(BaseVideoFile):
    """
    Represents a video file that has been encoded,
    with the purpose of analyzing encoder performance
    """

    REL_PATH_TO_OVF: str = "encoded/"

    class Meta:
        unique_together = ("original_video_file", "encoder_setting")

    original_video_file = models.ForeignKey(
        OriginalVideoFile,
        on_delete=models.CASCADE,
        related_name="encoded_video_files",
    )

    encoder_setting = models.ForeignKey(
        "EncoderSetting",
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
        """
        Calls ffmpeg with the expected arguments,
        starting the encoding process
        """
        if self.encoding_time:
            return
        self.encoding_time = FFMPEG.call(
            [
                "-y",
                "-loglevel",
                "warning",
                "-i",
                f'"{self.original_video_file.file_path}"',
            ]
            + self.encoder_setting.ffmpeg_args
            + [self.file_path]
        )[0]
        self.encoding_time = round(self.encoding_time, 5)
        self.save(update_fields=["encoding_time"])


class DecodedVideoFile(BaseVideoFile):
    """
    Represents an EncodedVideoFIle that has been decoded,
    with the purpose of analyzing the quality difference between
    itself and its associated OriginalVideoFile
    """

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
        self.compute_comparison_metrics()

        # delete decoded video from disk after
        # extracting metadata and computing metrics
        remove_file_tree(self.file_path)

    def compute_comparison_metrics(self) -> None:
        """
        Responsible for starting the computation process
        for each associated ComparisonFilterResult
        """
        logger.info(f"Computing comparison metrics for {self}")
        cfrs = self.filter_results.filter(value__isnull=True)
        if cfrs:
            for cfr in cfrs:
                cfr.compute()

    def decode(self) -> None:
        """
        Calls ffmpeg with the expected arguments,
        starting the decoding process
        """
        if not self.decoding_time:
            self.decoding_time = Decode.call(
                input_file_path=self.encoded_video_file.file_path,
                output_file_path=self.file_path,
            )
            self.save(update_fields=["decoding_time"])
