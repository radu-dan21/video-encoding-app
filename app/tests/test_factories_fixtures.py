import pytest

from tests.factories import EncoderSettingFactory
from video_coding.entities.models import DecodedVideoFile, EncoderSetting


@pytest.mark.django_db
def test_encoder_setting_factory():
    EncoderSettingFactory.create()
    assert EncoderSetting.objects.count() == 1


@pytest.mark.django_db
def test_dvf_fixture(dvf):
    assert DecodedVideoFile.objects.count() == 1
