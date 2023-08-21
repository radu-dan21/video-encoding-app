from django.db import models

from video_coding.entities.models.base import BaseModel


class BDMetric(BaseModel):
    original_video_file = models.ForeignKey(
        "OriginalVideoFile",
        on_delete=models.CASCADE,
        related_name="bd_metrics",
    )
    video_filter = models.ForeignKey(
        "ComparisonFilter",
        on_delete=models.CASCADE,
    )
    reference_codec = models.ForeignKey(
        "Codec",
        on_delete=models.CASCADE,
        related_name="reference_metrics",
    )
    test_codec = models.ForeignKey(
        "Codec",
        on_delete=models.CASCADE,
        related_name="test_metrics",
    )
    bd_rate = models.FloatField()
    bd_metric = models.FloatField()
