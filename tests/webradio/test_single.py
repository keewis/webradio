import pathlib
import shutil
import subprocess

from unittest import mock
import pytest

import gc

import webradio.single as single


@pytest.fixture(scope='module')
def disable_gc():
    gc.disable()


@pytest.fixture(scope='function')
def call():
    m = mock.patch(
        'webradio.single.subprocess.call',
        mock.create_autospec(subprocess.call),
        )

    with m as call:
        yield call


@pytest.fixture(scope='function')
def rmtree():
    m = mock.patch(
        'webradio.single.shutil.rmtree',
        mock.create_autospec(shutil.rmtree),
        )

    with m as rmtree:
        yield rmtree


@pytest.fixture(scope='function')
def exists():
    m = mock.patch(
        'webradio.single.pathlib.Path.exists',
        mock.create_autospec(pathlib.Path.exists),
        )

    with m as exists:
        yield exists


@pytest.fixture(scope='function')
def mkdir():
    m = mock.patch(
        'webradio.single.pathlib.Path.mkdir',
        mock.create_autospec(pathlib.Path.mkdir),
        )

    with m as mkdir:
        yield mkdir


@pytest.fixture(scope='function')
def rmdir():
    m = mock.patch(
        'webradio.single.pathlib.Path.rmdir',
        mock.create_autospec(pathlib.Path.rmdir),
        )

    with m as rmdir:
        yield rmdir


@pytest.fixture(scope='function')
def fill():
    m = mock.patch(
        'webradio.single.fill',
        mock.create_autospec(single.fill),
        )

    with m as fill:
        yield fill


def test_fill(tmpdir):
    path = pathlib.Path(str(tmpdir))

    single.fill(path)

    mpd = path / "mpd"
    assert mpd.is_dir()
    expected_content = [
        mpd / name
        for name in ["database", "mpd.conf", "playlists"]
        ]
    assert sorted(mpd.iterdir()) == expected_content
    config = mpd / "mpd.conf"
    assert (mpd / "playlists").is_dir()
    assert config.is_file() and (mpd / "database").is_file()
    assert config.stat().st_size > 0


class TestServer(object):
    def test_init_succeeding(self, exists, mkdir, fill, call):
        basepath = pathlib.Path("root")

        exists.return_value = False
        s = single.Server(basepath=basepath)
        assert call.call_count == 1
        del s

    def test_init_failing(self, exists, mkdir, fill, call):
        basepath = pathlib.Path("root")

        exists.return_value = True
        with pytest.raises(FileExistsError):
            single.Server(basepath=basepath)
        assert call.call_count == 0

    def test_destroy_succeeding(
            self,
            exists,
            mkdir,
            fill,
            call,
            rmtree,
            rmdir,
            ):
        basepath = pathlib.Path("root").absolute()

        exists.return_value = False
        s = single.Server(basepath=basepath)
        exists.return_value = True

        del s
        assert call.call_count == 2
        assert "--kill" in call.call_args_list[1][0][0]
        assert rmtree.call_args_list == [mock.call(str(basepath / "mpd"))]
        assert rmdir.call_args_list == [mock.call(basepath)]

    def test_destroy_failing(self, exists, mkdir, fill, call, rmtree):
        basepath = pathlib.Path("root")
        exists.return_value = False

        # first fail
        s = single.Server(basepath=basepath)
        exists.return_value = False
        del s
        assert rmtree.call_count == 0

        # second fail
        s = single.Server(basepath=basepath)
        exists.return_value = True
        rmtree.side_effect = FileNotFoundError
        del s
        assert rmtree.call_count == 1
