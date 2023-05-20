from __future__ import annotations

import logging

from abc import abstractmethod

from django.db import models
from django_jsonform.models.fields import ArrayField

from video_coding.entities.models.base import BaseModel
from video_coding.entities.models.video_file import DecodedVideoFile, OriginalVideoFile
from video_coding.utils.ffmpeg import FFMPEG


logger = logging.getLogger(__name__)


class Filter(BaseModel):
    ffmpeg_args = ArrayField(
        models.CharField(max_length=BaseModel.MAX_CHAR_FIELD_LEN),
    )


class ComparisonFilter(Filter):
    ...


class InformationFilter(Filter):
    ...


class FilterResults(BaseModel):
    FFMPEG_CMD_SUFFIX = "-f null - |& tac 2>&1 | sed -n '0,/Parsed/p' | tac"

    video_filter = models.ForeignKey(
        Filter,
        on_delete=models.CASCADE,
        related_name="results",
    )

    output = models.CharField(
        max_length=1024,
        blank=True,
        default=True,
    )

    compute_time = models.FloatField(null=True)

    def call_ffmpeg(self, args: list[str]) -> str | None:
        self.compute_time, output = FFMPEG.call(
            args + self.FFMPEG_CMD_SUFFIX.split(" "),
        )
        self.output = output
        self.save(update_fields=["compute_time", "output"])

    @abstractmethod
    def compute(self) -> None:
        logger.info(f"Computing filter {self}")
        ...


class ComparisonFilterResult(FilterResults):
    video_to_compare = models.ForeignKey(
        DecodedVideoFile,
        on_delete=models.CASCADE,
    )

    reference_video = models.ForeignKey(
        OriginalVideoFile,
        on_delete=models.CASCADE,
        related_name="comparison_filter_results",
    )

    def compute(self) -> None:
        args: list[str] = [
            "-i",
            self.video_to_compare.file_path,
            "-i",
            self.reference_video.file_path,
        ] + self.video_filter.ffmpeg_args
        self.call_ffmpeg(args)


class InformationFilterResult(FilterResults):
    video = models.ForeignKey(
        OriginalVideoFile,
        on_delete=models.CASCADE,
        related_name="info_filter_results",
    )

    def compute(self) -> None:
        args: list[str] = ["-i", self.video.file_path] + self.video_filter.ffmpeg_args
        self.call_ffmpeg(args)
