import os.path

import pytest

from video_coding.entities.models import (
    BaseVideoFile,
    ComparisonFilter,
    ComparisonFilterResult,
    DecodedVideoFile,
    EncodedVideoFile,
    InformationFilter,
    InformationFilterResult,
    OriginalVideoFile,
    VideoEncoding,
)
from video_coding.workflows import revert_back


@pytest.mark.django_db
class TestMainWorkflow:
    @staticmethod
    def _get_all_video_files(ovf: OriginalVideoFile) -> list[BaseVideoFile]:
        evfs: list[EncodedVideoFile] = list(ovf.encoded_video_files.all())
        return [ovf] + evfs

    def test_main_workflow_successful(
        self,
        test_ovf: OriginalVideoFile,
        av1: VideoEncoding,
        hevc: VideoEncoding,
        siti: InformationFilter,
        psnr: ComparisonFilter,
        prepare_main_workflow: callable,
    ):
        prepare_main_workflow(test_ovf, [av1, hevc], [siti], [psnr])
        test_ovf.run_workflow()

        def is_vf_successfully_processed(vf: BaseVideoFile) -> bool:
            return bool(vf) and bool(vf.ffprobe_info) and os.path.exists(vf.file_path)

        video_files: list[BaseVideoFile] = self._get_all_video_files(test_ovf)
        assert all(is_vf_successfully_processed(vf) for vf in video_files)

        revert_back(test_ovf.id)
        self._assert_rollback_successful(test_ovf, video_files)

    @staticmethod
    def _assert_rollback_successful(
        ovf: OriginalVideoFile,
        old_video_files: list[BaseVideoFile],
    ) -> None:
        old_video_files.remove(ovf)
        assert not any(os.path.exists(vf.parent_dir) for vf in old_video_files)

        ovf.refresh_from_db()
        assert not ovf.ffprobe_info
        assert ovf.status == OriginalVideoFile.Status.READY

        assert all(
            model.objects.count() == 0
            for model in (
                ComparisonFilterResult,
                InformationFilterResult,
                EncodedVideoFile,
                DecodedVideoFile,
            )
        )

    def test_main_workflow_fails(
        self,
        test_ovf: OriginalVideoFile,
        av1: VideoEncoding,
        hevc: VideoEncoding,
        siti: InformationFilter,
        psnr: ComparisonFilter,
        prepare_main_workflow: callable,
    ):
        prepare_main_workflow(test_ovf, [av1, hevc], [siti], [psnr])
        test_ovf.file_name = "video_that_does_not_exist.mp4"
        test_ovf.save(update_fields=["file_name"])

        with pytest.raises(Exception):
            test_ovf.run_workflow()

        test_ovf.refresh_from_db()
        assert test_ovf.status == OriginalVideoFile.Status.FAILED
        assert bool(test_ovf.error_message)
