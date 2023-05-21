from django.contrib import admin

from video_coding.entities.models import (
    ComparisonFilter,
    ComparisonFilterResult,
    DecodedVideoFile,
    EncodedVideoFile,
    InformationFilter,
    InformationFilterResult,
    OriginalVideoFile,
    VideoEncoding,
)


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
