import os

import pytest

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
from video_coding.workflows import PrepareMainWorkflow, revert_back


@pytest.mark.django_db
class TestPrepareMainWorkflow:
    @staticmethod
    def _run_workflow(
        ovf: OriginalVideoFile,
        encodings: list[VideoEncoding],
        info_filters: list[InformationFilter],
        comp_filters: list[ComparisonFilter],
    ) -> None:
        PrepareMainWorkflow(
            ovf.id,
            [e.id for e in encodings],
            [i.id for i in info_filters],
            [c.id for c in comp_filters],
        ).run()

    def test_prepare_main_worflow(self, ovf, encodings, info_filter, comp_filter):
        self._run_workflow(ovf, encodings, [info_filter], [comp_filter])
        ovf.refresh_from_db()

        evfs: list[EncodedVideoFile] = list(ovf.encoded_video_files.all())
        assert len(evfs) == len(encodings)

        dvfs: list[DecodedVideoFile] = [evf.decoded_video_file for evf in evfs]
        assert not any(dvf is None for dvf in dvfs)

        assert ovf.info_filter_results.count() == 1
        assert ovf.comparison_filter_results.count() == len(encodings)

        assert all(
            os.path.exists(parent_dir)
            for parent_dir in (vf.parent_dir for vf in [ovf] + evfs + dvfs)
        )

    def test_revert_back(self, ovf, encodings, info_filter, comp_filter):
        self._run_workflow(ovf, encodings, [info_filter], [comp_filter])
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
