from pytest import fixture

from tests.factories import (
    ComparisonFilterFactory,
    DecodedVideoFileFactory,
    InformationFilterFactory,
    OriginalVideoFileFactory,
    VideoEncodingFactory,
)


@fixture
def ovf():
    return OriginalVideoFileFactory.create()


@fixture
def dvf():
    return DecodedVideoFileFactory.create()


@fixture
def encodings():
    return VideoEncodingFactory.create_batch(2)


@fixture
def comp_filter():
    return ComparisonFilterFactory.create()


@fixture
def info_filter():
    return InformationFilterFactory.create()
