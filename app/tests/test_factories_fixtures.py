import pytest

from tests.factories import VideoEncodingFactory
from video_coding.entities.models import DecodedVideoFile, VideoEncoding


@pytest.mark.django_db
def test_video_encoding_factory():
    VideoEncodingFactory.create()
    assert VideoEncoding.objects.count() == 1


@pytest.mark.django_db
def test_dvf_fixture(dvf):
    assert DecodedVideoFile.objects.count() == 1
