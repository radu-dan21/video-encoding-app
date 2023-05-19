from __future__ import annotations

from abc import abstractmethod

from django.db import models
from django_jsonform.models.fields import ArrayField, JSONField

from video_coding.entities.models.base import BaseModel
from video_coding.entities.models.video_file import DecodedVideoFile, OriginalVideoFile
from video_coding.utils.ffmpeg import FFMPEG


class Filter(BaseModel):
    ffmpeg_args = ArrayField(
        models.CharField(max_length=BaseModel.MAX_CHAR_FIELD_LEN),
    )


class ComparisonFilter(Filter):
    ...


class InformationFilter(Filter):
    ...


class FilterResults(BaseModel):
    video_filter = models.ForeignKey(
        Filter,
        on_delete=models.CASCADE,
        related_name="results",
    )

    json_output = JSONField(
        null=True,
        blank=True,
    )

    compute_time = models.FloatField(null=True)

    def call_ffmpeg(self, args: list[str]) -> bytes | None:
        self.compute_time, output = FFMPEG.call(args, capture_output=True)
        self.save(update_fields=["compute_time"])
        return output

    @abstractmethod
    def compute(self) -> None:
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
        ...
        # TODO: need to return ffmpeg output in order to save it
        # self.call_ffmpeg()


class InformationFilterResult(FilterResults):
    video = models.ForeignKey(
        OriginalVideoFile,
        on_delete=models.CASCADE,
        related_name="info_filter_results",
    )

    def compute(self) -> None:
        ...
