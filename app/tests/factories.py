import factory

from video_coding.entities import models


FFMPEG_TEST_ARGS = ["-foo", "bar"]


class BaseModelFactory(factory.django.DjangoModelFactory):
    name = factory.LazyAttributeSequence(lambda o, i: f"{o.__class__.__name__}_{i}")


class VideoEncodingFactory(BaseModelFactory):
    class Meta:
        model = models.VideoEncoding

    ffmpeg_args = factory.List(FFMPEG_TEST_ARGS)


class BaseVideoFileFactory(BaseModelFactory):
    file_name = factory.LazyAttribute(lambda o: f"{o.name}.mp4")


class OriginalVideoFileFactory(BaseVideoFileFactory):
    class Meta:
        model = models.OriginalVideoFile


class EncodedVideoFileFactory(BaseVideoFileFactory):
    class Meta:
        model = models.EncodedVideoFile

    original_video_file = factory.SubFactory(OriginalVideoFileFactory)
    video_encoding = factory.SubFactory(VideoEncodingFactory)


class DecodedVideoFileFactory(BaseVideoFileFactory):
    class Meta:
        model = models.DecodedVideoFile

    encoded_video_file = factory.SubFactory(EncodedVideoFileFactory)


class BaseFilterFactory(BaseModelFactory):
    ffmpeg_args = factory.List(FFMPEG_TEST_ARGS)


class InformationFilterFactory(BaseFilterFactory):
    class Meta:
        model = models.InformationFilter


class ComparisonFilterFactory(BaseFilterFactory):
    class Meta:
        model = models.ComparisonFilter


class InformationFilterResultsFactory(BaseModelFactory):
    class Meta:
        model = models.InformationFilterResult

    video = factory.SubFactory(OriginalVideoFileFactory)
    video_filter = factory.SubFactory(InformationFilterFactory)


class ComparisonFilterResultsFactory(BaseModelFactory):
    class Meta:
        model = models.ComparisonFilterResult

    video_to_compare = factory.SubFactory(DecodedVideoFileFactory)
    reference_video = factory.LazyAttribute(
        lambda o: o.video_to_compare.encoded_video_file.original_video_file,
    )
    video_filter = factory.SubFactory(ComparisonFilterFactory)
