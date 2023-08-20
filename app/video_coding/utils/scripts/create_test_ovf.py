import os

from django.conf import settings

from video_coding.entities.models import OriginalVideoFile, VideoEncoding
from video_coding.tasks import run_ovf_workflow
from video_coding.workflows import PrepareMainWorkflow


selected_encoding_names = [
    "AV1 - preset 5 - CRF 63",
    "HEVC - preset slow - CRF 44",
    "AV1 - preset 5 - CRF 25",
    "HEVC - preset slow - CRF 20",
    "AV1 - preset 5 - CRF 38",
    "HEVC - preset slow - CRF 27",
    "AV1 - preset 5 - CRF 54",
    "HEVC - preset slower - CRF 34",
    "AV1 - preset 5 - CRF 46",
    "HEVC - preset slow - CRF 30",
    "AV1 - preset 4 - CRF 38",
    "HEVC - preset slower - CRF 27",
    "AV1 - preset 5 - CRF 50",
    "HEVC - preset slow - CRF 34",
    "AV1 - preset 4 - CRF 21",
    "HEVC - preset slower - CRF 17",
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
