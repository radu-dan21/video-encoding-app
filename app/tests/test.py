import pytest

from tests.factories import VideoEncodingFactory
from video_coding.entities.models import DecodedVideoFile, VideoEncoding


@pytest.mark.django_db
def test_video_encoding_factory():
    ve = VideoEncodingFactory.create()
    video_encodings = VideoEncoding.objects.all()
    assert len(video_encodings) == 1
    assert next(iter(video_encodings)) == ve


@pytest.mark.django_db
def test_dvf_fixture(dvf):
    dvfs = DecodedVideoFile.objects.all()
    assert len(dvfs) == 1
    assert next(iter(dvfs)) == dvf
