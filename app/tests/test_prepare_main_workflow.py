import os

import pytest

from video_coding.entities.models import (
    ComparisonFilter,
    ComparisonFilterResult,
    DecodedVideoFile,
    EncodedVideoFile,
    EncoderSetting,
    InformationFilter,
    InformationFilterResult,
    OriginalVideoFile,
)
from video_coding.workflows import revert_back


@pytest.mark.django_db
class TestPrepareMainWorkflow:
    def test_prepare_main_workflow(
        self,
        ovf: OriginalVideoFile,
        encoder_settings: list[EncoderSetting],
        info_filter: InformationFilter,
        comp_filter: ComparisonFilter,
        prepare_main_workflow: callable,
    ):
        prepare_main_workflow(ovf, encoder_settings, [info_filter], [comp_filter])
        ovf.refresh_from_db()

        evfs: list[EncodedVideoFile] = list(ovf.encoded_video_files.all())
        assert len(evfs) == len(encoder_settings)

        dvfs: list[DecodedVideoFile] = [evf.decoded_video_file for evf in evfs]
        assert not any(dvf is None for dvf in dvfs)

        assert ovf.info_filter_results.count() == 1
        assert ovf.comparison_filter_results.count() == len(encoder_settings)

        assert all(
            os.path.exists(parent_dir)
            for parent_dir in (vf.parent_dir for vf in [ovf] + evfs + dvfs)
        )

    def test_revert_back(
        self,
        ovf: OriginalVideoFile,
        encoder_settings: list[EncoderSetting],
        info_filter: InformationFilter,
        comp_filter: ComparisonFilter,
        prepare_main_workflow: callable,
    ):
        prepare_main_workflow(ovf, encoder_settings, [info_filter], [comp_filter])
        ovf.status = OriginalVideoFile.Status.FAILED
        ovf.save(update_fields=["status"])

        revert_back(ovf.id)

        assert all(
            model.objects.count() == 0
            for model in [
                EncodedVideoFile,
                DecodedVideoFile,
                InformationFilterResult,
                ComparisonFilterResult,
            ]
        )

        ovf.refresh_from_db()
        assert ovf.status == OriginalVideoFile.Status.READY
        assert os.path.exists(ovf.parent_dir)
        assert os.listdir(ovf.parent_dir) == []
