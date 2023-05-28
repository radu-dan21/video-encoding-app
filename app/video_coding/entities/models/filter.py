from __future__ import annotations

import logging

from abc import abstractmethod

from django.db import models
from django_jsonform.models.fields import ArrayField

from video_coding.entities.models.base import BaseModel
from video_coding.entities.models.video_file import DecodedVideoFile, OriginalVideoFile
from video_coding.utils import FFMPEG


logger = logging.getLogger(__name__)


class Filter(BaseModel):
    class Meta:
        abstract = True

    ffmpeg_args = ArrayField(
        models.CharField(max_length=BaseModel.MAX_CHAR_FIELD_LEN),
    )


class InformationFilter(Filter):
    ...


class ComparisonFilter(Filter):
    ...


class FilterResults(BaseModel):
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

    def call_ffmpeg(self, args: list[str]) -> str | None:
        self.compute_time, self.output = FFMPEG.call(
            args + self.FFMPEG_CMD_SUFFIX.split(" "),
        )
        self.compute_time = round(self.compute_time, 2)
        self.save(update_fields=["compute_time", "output"])


class InformationFilterResult(FilterResults):
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

    def compute(self) -> None:
        args: list[str] = [
            "-i",
            f'"{self.video_to_compare.file_path}"',
            "-i",
            f'"{self.reference_video.file_path}"',
        ] + self.video_filter.ffmpeg_args
        self.call_ffmpeg(args)
