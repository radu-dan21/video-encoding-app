from __future__ import annotations

import logging
import re

from abc import abstractmethod

from django.db import models
from django_jsonform.models.fields import ArrayField

from video_coding.entities.models.base import BaseModel
from video_coding.entities.models.video_file import DecodedVideoFile, OriginalVideoFile
from video_coding.utils import FFMPEG


logger = logging.getLogger(__name__)


class Filter(BaseModel):
    """
    Base class that defines the common behavior of
    all types of video metrics used throughout the project
    """

    class Meta:
        abstract = True

    ffmpeg_args = ArrayField(
        models.CharField(max_length=BaseModel.MAX_CHAR_FIELD_LEN),
        help_text="Arguments that will be passed to ffmpeg for metric computation.",
    )
    description = models.TextField(
        null=False,
        blank=True,
    )


class InformationFilter(Filter):
    """
    Represents a metric that provides information about a single video,
    which can be used for video classification
    """

    ...


class ComparisonFilter(Filter):
    """
    Represents a metric that provides information about the difference in quality,
    between an original video and its encoded variant
    """

    regex_for_value_extraction = models.CharField(
        max_length=BaseModel.MAX_CHAR_FIELD_LEN,
        help_text=(
            "Regular expression that will be used for extracting the quality "
            "score (float) from ffmpeg's output. Must include a capture group with "
            "the name 'value'."
        ),
    )


class FilterResults(BaseModel):
    """
    Base class that defines the common behavior of
    all types of metric results used throughout the project
    """

    class Meta:
        abstract = True

    # used for capturing (only) filter/metric output
    FFMPEG_CMD_SUFFIX: str = "-f null - |& tac 2>&1 | sed -n '0,/Parsed/p' | tac"

    output = models.TextField(
        blank=True,
        default="",
    )

    compute_time = models.FloatField(null=True)

    @abstractmethod
    def compute(self) -> None:
        logger.info(f"Computing filter {self}")
        ...

    def call_ffmpeg(self, args: list[str], commit=True) -> str | None:
        self.compute_time, self.output = FFMPEG.call(
            args + self.FFMPEG_CMD_SUFFIX.split(" "),
        )
        self.compute_time = round(self.compute_time, 5)
        if commit:
            self.save(update_fields=["compute_time", "output"])


class InformationFilterResult(FilterResults):
    """
    Represents the result of an InformationFilter, for an OriginalVideoFile instance
    """

    video_filter = models.ForeignKey(
        InformationFilter,
        on_delete=models.CASCADE,
        related_name="results",
    )

    video = models.ForeignKey(
        OriginalVideoFile,
        on_delete=models.CASCADE,
        related_name="info_filter_results",
    )

    def compute(self) -> None:
        args: list[str] = [
            "-i",
            f'"{self.video.file_path}"',
        ] + self.video_filter.ffmpeg_args
        self.call_ffmpeg(args)


class ComparisonFilterResult(FilterResults):
    """
    Represents the result of an ComparisonFilter, for an OriginalVideoFile instance and
    one of its encoded variants, after it has been decoded
    """

    video_filter = models.ForeignKey(
        ComparisonFilter,
        on_delete=models.CASCADE,
        related_name="results",
    )

    reference_video = models.ForeignKey(
        OriginalVideoFile,
        on_delete=models.CASCADE,
        related_name="comparison_filter_results",
    )

    video_to_compare = models.ForeignKey(
        DecodedVideoFile,
        on_delete=models.CASCADE,
        related_name="filter_results",
    )

    value = models.FloatField(null=True)

    def compute(self) -> None:
        args: list[str] = [
            "-i",
            f'"{self.video_to_compare.file_path}"',
            "-i",
            f'"{self.reference_video.file_path}"',
        ] + self.video_filter.ffmpeg_args
        self.call_ffmpeg(args)

    def call_ffmpeg(self, args: list[str], commit=True) -> str | None:
        super().call_ffmpeg(args, commit=False)
        match = re.search(self.video_filter.regex_for_value_extraction, self.output)
        self.value = float(match.group("value"))
        self.save()
