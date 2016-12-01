import pathlib
import pytest
from unittest import mock

import frontend.utils as utils


@pytest.fixture(scope='function')
def mkdtemp():
    m = mock.patch(
        'frontend.utils.tempfile.mkdtemp',
        mock.create_autospec(utils.tempfile.mkdtemp),
        )

    with m as mkdtemp:
        yield mkdtemp


@pytest.fixture(scope='function')
def rmdir():
    m = mock.patch(
        'frontend.utils.pathlib.Path.rmdir',
        mock.create_autospec(utils.pathlib.Path.rmdir),
        )

    with m as rmdir:
        yield rmdir


def test_basepath(mkdtemp, rmdir):
    base = '/tmp'
    suffix = "jkl.mno"

    tmppath = pathlib.Path('/tmp/def/ghi')
    mkdtemp.return_value = tmppath

    with utils.basepath(suffix=suffix) as path:
        assert str(path) == str(tmppath / suffix)

    assert mkdtemp.call_args_list[-1] == mock.call(dir=base)
    assert rmdir.call_args_list[-1] == mock.call(tmppath)
