import os
import shutil

from pytest import fixture

from tests.factories import (
    ComparisonFilterFactory,
    DecodedVideoFileFactory,
    EncoderFactory,
    EncoderSettingFactory,
    InformationFilterFactory,
    OriginalVideoFileFactory,
)
from video_coding.entities.models import (
    ComparisonFilter,
    DecodedVideoFile,
    Encoder,
    EncoderSetting,
    InformationFilter,
    OriginalVideoFile,
)
from video_coding.workflows import PrepareMainWorkflow


def rm_folder_structure_sync(ovf) -> None:
    shutil.rmtree(ovf.parent_dir, ignore_errors=True)


@fixture(autouse=True)
def delete_files_sync(mocker):
    rm_folder_structure: str = (
        "video_coding.entities.models.video_file."
        "BaseVideoFile.remove_folder_structure"
    )
    mocker.patch(rm_folder_structure, rm_folder_structure_sync)


@fixture
def ovf() -> OriginalVideoFile:
    return OriginalVideoFileFactory.create()


@fixture
def dvf() -> DecodedVideoFile:
    return DecodedVideoFileFactory.create()


@fixture
def encoder_settings() -> list[EncoderSetting]:
    return EncoderSettingFactory.create_batch(2)


@fixture
def comp_filter() -> ComparisonFilter:
    return ComparisonFilterFactory.create()


@fixture
def info_filter() -> InformationFilter:
    return InformationFilterFactory.create()


@fixture
def prepare_main_workflow() -> callable:
    return _prepare_main_workflow


def _prepare_main_workflow(
    ovf: OriginalVideoFile,
    encodings: list[EncoderSetting],
    info_filters: list[InformationFilter],
    comp_filters: list[ComparisonFilter],
) -> None:
    PrepareMainWorkflow(
        ovf.id,
        [e.id for e in encodings],
        [i.id for i in info_filters],
        [c.id for c in comp_filters],
    ).run()


@fixture
def av1_encoder() -> Encoder:
    return EncoderFactory.create(
        name="AV1",
        ffmpeg_args=["-c:v", "libsvtav1"],
    )


@fixture
def hevc_encoder() -> Encoder:
    return EncoderFactory.create(
        name="HEVC",
        ffmpeg_args=["-c:v", "libx265"],
    )


@fixture
def av1(av1_encoder) -> EncoderSetting:
    return EncoderSettingFactory.create(
        name="AV1",
        encoder=av1_encoder,
        extra_ffmpeg_args=["-crf", "30"],
        video_extension="mkv",
    )


@fixture
def hevc(hevc_encoder) -> EncoderSetting:
    return EncoderSettingFactory.create(
        name="HEVC",
        encoder=hevc_encoder,
        extra_ffmpeg_args=["-crf", "30"],
        video_extension="mkv",
    )


@fixture
def siti() -> InformationFilter:
    return InformationFilterFactory.create(
        name="SITI",
        ffmpeg_args=[
            "-vf",
            "siti=print_summary=1",
        ],
    )


@fixture
def psnr() -> ComparisonFilter:
    return ComparisonFilterFactory.create(
        name="PSNR",
        ffmpeg_args=[
            "-filter_complex",
            "psnr",
        ],
        regex_for_value_extraction=".+average:(?P<value>[^ ]+) .+",
    )


@fixture
def test_ovf() -> OriginalVideoFile:
    ovf = OriginalVideoFileFactory.create(file_name="test.mkv")
    shutil.copyfile(os.environ.get("TEST_OVF_PATH"), ovf.file_path)
    yield ovf
    shutil.rmtree(ovf.parent_dir)
