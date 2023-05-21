import pytest

from video_coding.entities.models import VideoEncoding


@pytest.mark.django_db
def test_create_video_encoding():
    VideoEncoding.objects.create(name="foo", ffmpeg_args=["bar"])
    assert VideoEncoding.objects.count() == 1
