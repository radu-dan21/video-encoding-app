from pytest import fixture

from tests.factories import DecodedVideoFileFactory, OriginalVideoFileFactory


@fixture
def ovf():
    return OriginalVideoFileFactory.create()


@fixture
def dvf():
    return DecodedVideoFileFactory.create()
