from __future__ import annotations

from django.db import models
from django_jsonform.models.fields import ArrayField, JSONField

from video_coding.entities.models.base import BaseModel
from video_coding.entities.models.video_file import DecodedVideoFile, OriginalVideoFile


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


class ComparisonFilterResults(FilterResults):
    video_to_compare = models.ForeignKey(
        DecodedVideoFile,
        on_delete=models.CASCADE,
    )

    reference_video = models.ForeignKey(
        OriginalVideoFile,
        on_delete=models.CASCADE,
    )


class InformationFilterResults(FilterResults):
    video = models.ForeignKey(
        OriginalVideoFile,
        on_delete=models.CASCADE,
        related_name="info_filter_results",
    )
