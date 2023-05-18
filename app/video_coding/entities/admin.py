from django.contrib import admin

from video_coding.entities.models import (
    EncodedVideoFile,
    Filter,
    OriginalVideoFile,
    VideoEncoding,
)


@admin.register(EncodedVideoFile)
class EncodedVideoFileAdmin(admin.ModelAdmin):
    pass


@admin.register(Filter)
class FilterAdmin(admin.ModelAdmin):
    pass


@admin.register(OriginalVideoFile)
class OriginalVideoFileAdmin(admin.ModelAdmin):
    pass


@admin.register(VideoEncoding)
class VideoEncodingAdmin(admin.ModelAdmin):
    pass
