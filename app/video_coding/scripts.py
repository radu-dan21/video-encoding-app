import os

from django.conf import settings

from video_coding.entities.models import OriginalVideoFile, VideoEncoding
from video_coding.tasks import run_ovf_workflow
from video_coding.workflows import PrepareMainWorkflow


selected_encoding_names = [
    "AV1 - preset 4 - CRF 17",
    "HEVC - preset slow - CRF 17",
    "AV1 - preset 5 - CRF 34",
    "HEVC - preset slower - CRF 23",
    "AV1 - preset 4 - CRF 5",
    "HEVC - preset slow - CRF 10",
    "AV1 - preset 4 - CRF 13",
    "HEVC - preset slower - CRF 13",
    "AV1 - preset 5 - CRF 21",
    "HEVC - preset slower - CRF 20",
    "AV1 - preset 4 - CRF 9",
    "HEVC - preset slow - CRF 13",
    "AV1 - preset 4 - CRF 1",
    "HEVC - preset slow - CRF 6",
    "AV1 - preset 5 - CRF 5",
    "HEVC - preset slower - CRF 10",
]


def create_test_ovf(
    ovf_name: str,
    file_name: str,
) -> None:
    video_path: str = os.path.join(
        settings.VIDEOS_FOR_PROCESSING_PATH,
        file_name,
    )
    ovf = OriginalVideoFile.objects.create(name=ovf_name, file_name=file_name)
    pmw = PrepareMainWorkflow(
        ovf_id=ovf.id,
        encoding_ids=list(
            VideoEncoding.objects.filter(name__in=selected_encoding_names).values_list(
                "id", flat=True
            )
        ),
        info_filter_ids=[1],
        comparison_filter_ids=[1, 2],
    )
    pmw.run()
    run_ovf_workflow.delay(ovf_id=ovf.id, file_path=video_path)
