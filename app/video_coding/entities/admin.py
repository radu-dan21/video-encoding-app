from django.contrib import admin

from video_coding.entities.models import (
    BDMetric,
    Codec,
    ComparisonFilter,
    ComparisonFilterResult,
    DecodedVideoFile,
    EncodedVideoFile,
    EncodingTimeGraph,
    InformationFilter,
    InformationFilterResult,
    MetricGraph,
    OriginalVideoFile,
    VideoEncoding,
)


@admin.register(BDMetric)
class BDMetricAdmin(admin.ModelAdmin):
    def get_form(self, request, obj=None, **kwargs):
        help_texts = {
            "bd_rate": (
                "Average changes in bitrate for the test encoder, "
                "compared to the reference encoder (expressed as a percentage)."
            ),
            "bd_metric": (
                "Average changes in the specified quality metric "
                "for the test encoder, compared to the reference encoder."
            ),
        }
        kwargs.update({"help_texts": help_texts})
        return super().get_form(request, obj, **kwargs)


@admin.register(Codec)
class CodecAdmin(admin.ModelAdmin):
    pass


@admin.register(ComparisonFilter)
class ComparisonFilterAdmin(admin.ModelAdmin):
    pass


@admin.register(ComparisonFilterResult)
class ComparisonFilterResultsAdmin(admin.ModelAdmin):
    pass


@admin.register(DecodedVideoFile)
class DecodedVideoFileAdmin(admin.ModelAdmin):
    pass


@admin.register(EncodedVideoFile)
class EncodedVideoFileAdmin(admin.ModelAdmin):
    pass


@admin.register(EncodingTimeGraph)
class EncodingTimeGraphAdmin(admin.ModelAdmin):
    pass


@admin.register(MetricGraph)
class MetricGraphAdmin(admin.ModelAdmin):
    pass


@admin.register(InformationFilter)
class InformationFilterAdmin(admin.ModelAdmin):
    pass


@admin.register(InformationFilterResult)
class InformationFilterResultsAdmin(admin.ModelAdmin):
    pass


@admin.register(OriginalVideoFile)
class OriginalVideoFileAdmin(admin.ModelAdmin):
    pass


@admin.register(VideoEncoding)
class VideoEncodingAdmin(admin.ModelAdmin):
    pass
