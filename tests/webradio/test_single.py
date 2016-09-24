import pathlib
import shutil
import subprocess

from unittest import mock
import pytest

import gc

import webradio.single as single


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


@pytest.fixture(scope='function')
def mpdclient():
    m = mock.patch(
        'webradio.single.musicpd.MPDClient',
        mock.create_autospec(single.musicpd.MPDClient),
        )

    with m as mpdclient:
        yield mpdclient


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

    def test_shutdown_succeeding(
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

        s.shutdown()
        assert call.call_count == 2
        assert "--kill" in call.call_args_list[1][0][0]
        assert rmtree.call_args_list == [mock.call(str(basepath / "mpd"))]
        assert rmdir.call_args_list == [mock.call(basepath)]

    def test_shutdown_failing(self, exists, mkdir, fill, call, rmtree, rmdir):
        basepath = pathlib.Path("root")
        exists.return_value = False

        # first fail: basepath does not exist
        s1 = single.Server(basepath=basepath)

        exists.return_value = False
        rmtree.side_effect = FileNotFoundError
        s1.shutdown()

        assert rmtree.call_count == 1
        assert "--kill" not in call.call_args_list[-1][0][0]
        assert rmdir.call_count == 0

        rmtree.reset_mock()
        call.reset_mock()
        rmdir.reset_mock()

        # second fail: mpd exists, but basepath is not empty
        s2 = single.Server(basepath=basepath)

        exists.return_value = True
        rmtree.side_effect = None
        rmdir.side_effect = OSError

        s2.shutdown()
        assert rmtree.call_count == 1
        assert "--kill" in call.call_args_list[-1][0][0]
        assert rmdir.call_count == 1

    def test_socket(self, exists, mkdir, fill, call, rmtree, rmdir):
        basepath = pathlib.Path("root").absolute()
        exists.return_value = False

        s = single.Server(basepath=basepath)

        socket = s.socket

        assert socket.relative_to(basepath) == pathlib.Path("mpd/socket")


class TestClient(object):
    basepath = pathlib.Path("root")

    def test_init(self, mpdclient):
        client_mock = mpdclient.return_value

        # default arguments
        client = single.Client(self.basepath)

        expected_calls = [
            mock.call(host=str(self.basepath.absolute()), port=0),
            ]
        assert client_mock.connect.call_args_list == expected_calls
        assert client.muted is False

        # explicit muted state
        muted = True
        client = single.Client(self.basepath, muted=muted)

        assert client.muted == muted

    def test_destroy(self, mpdclient):
        client_mock = mpdclient.return_value

        client = single.Client(self.basepath)
        client.disconnect()

        assert client_mock.disconnect.call_count == 1

    def test_connect(self, mpdclient):
        client_mock = mpdclient.return_value

        client = single.Client(self.basepath)
        client_mock.connect.reset_mock()

        client._connect()

        expected_call = mock.call(host=str(self.basepath.absolute()), port=0)
        assert client_mock.connect.call_args_list == [expected_call]

    def test_disconnect(self, mpdclient):
        client_mock = mpdclient.return_value

        client = single.Client(self.basepath)

        # succeeding
        client.disconnect()
        assert client_mock.disconnect.call_count == 1

        client_mock.disconnect.reset_mock()
        # failing
        client_mock.disconnect.side_effect = BrokenPipeError
        client.disconnect()

        assert client_mock.disconnect.call_count == 1

    def test_ensure_connection(self, mpdclient):
        client_mock = mpdclient.return_value

        client = single.Client(self.basepath)

        # succeeding
        client_mock.ping.return_value = True
        client.clear()
        assert client_mock.clear.call_count == 1

        client_mock.clear.reset_mock()
        client_mock.connect.reset_mock()
        # failing
        client_mock.ping.side_effect = BrokenPipeError
        client.clear()

        # check that the calls were actually executed
        assert client_mock.clear.call_count == 1
        assert client_mock.connect.call_count == 1
        assert client_mock.disconnect.call_count == 1

    def test_volume(self, mpdclient):
        client_mock = mpdclient.return_value

        volume1 = 20
        volume2 = 35
        volume3 = 50

        client_mock.status.return_value = {'volume': volume1}
        client = single.Client(self.basepath, muted=False)

        # initial volume
        assert client.volume == volume1

        # first change
        client.volume = volume2
        assert client.volume == volume2

        # second change
        client.volume = volume3
        assert client.volume == volume3

        # assert that the changes took effect on the server
        expected_calls = [mock.call(volume2), mock.call(volume3)]
        assert client_mock.setvol.call_args_list == expected_calls

    def test_urls(self, mpdclient):
        client_mock = mpdclient.return_value
        client = single.Client(self.basepath)

        urls1 = list(map(str, range(2, 7)))
        urls2 = list(map(str, range(5, 40)))

        # initial value
        assert client.urls == []

        # reassign once
        client.urls = urls1
        assert client.urls == urls1

        # reassign again
        client.urls = urls2
        assert client.urls == urls2

        # check the server state
        assert client_mock.clear.call_count == 2
        expected_calls = list(map(mock.call, urls1 + urls2))
        assert client_mock.add.call_args_list == expected_calls

    def test_add(self, mpdclient):
        client_mock = mpdclient.return_value

        # urls to add
        urls = list(map(str, range(5)))

        client = single.Client(self.basepath)
        for url in urls:
            client.add(url)

        assert client_mock.add.call_args_list == list(map(mock.call, urls))
        assert client._urls == urls

    def test_clear(self, mpdclient):
        client_mock = mpdclient.return_value

        urls = list(map(str, range(20)))
        client = single.Client(self.basepath)
        client.urls = urls
        client_mock.clear.reset_mock()

        client.clear()
        assert client_mock.clear.call_count == 1
        assert client._urls == []

    def test_play(self, mpdclient):
        client_mock = mpdclient.return_value

        length = 10
        urls = list(map(str, range(length)))

        client = single.Client(self.basepath)
        client.urls = urls

        # without index
        client.play()

        # succeeding
        succeeding_index = abs(length - 5)
        client.play(succeeding_index)

        # failing
        failing_index = length + 5
        with pytest.raises(RuntimeError):
            client.play(failing_index)

        # check the server state
        expected_calls = [mock.call(), mock.call(succeeding_index)]
        assert client_mock.play.call_args_list == expected_calls

    def test_muted(self, mpdclient):
        client_mock = mpdclient.return_value

        volume1 = 52
        volume2 = 31
        client_mock.status.return_value = {'volume': volume1}
        client = single.Client(self.basepath, muted=False)

        # unmuted to unmuted
        client.muted = False
        assert client.muted is False

        # unmuted to muted
        client.muted = True
        assert client.muted is True

        # muted to muted
        client.muted = True
        assert client.muted is True

        # muted to unmuted
        client.muted = False
        assert client.muted is False

        # check the server state
        expected_calls = [mock.call(0), mock.call(volume1)]
        assert client_mock.setvol.call_args_list == expected_calls

        client_mock.setvol.reset_mock()

        # check that the volume does behave correctly
        # change when unmuted
        client.volume = volume2

        # change when muted
        client.muted = True
        client.volume = volume1

        expected_calls = [mock.call(volume2), mock.call(0)]
        assert client_mock.setvol.call_args_list == expected_calls

        client_mock.setvol.reset_mock()
        # only now when unmuting, the volume should change back again
        client.muted = False
        assert client_mock.setvol.call_args_list == [mock.call(volume1)]

    def test_mute(self, mpdclient):
        client = single.Client(self.basepath, muted=False)
        client_mock = mpdclient.return_value

        # mute when unmuted
        client.mute()

        assert client.muted is True

        # mute when muted
        client.mute()
        assert client.muted is True

        # the volume should only have changed once
        assert client_mock.setvol.call_args_list == [mock.call(0)]

    def test_unmute(self, mpdclient):
        client_mock = mpdclient.return_value

        volume = 41
        client_mock.status.return_value = {'volume': volume}
        client = single.Client(self.basepath, muted=True)

        # unmute when muted
        client.unmute()
        assert client.muted is False

        # unmute when unmuted
        client.unmute()
        assert client.muted is False

        # the volume should only have changed once
        assert client_mock.setvol.call_args_list == [mock.call(volume)]

    def test_toggle_mute(self, mpdclient):
        client_mock = mpdclient.return_value

        volume = 54
        client_mock.status.return_value = {'volume': volume}
        client = single.Client(self.basepath, muted=False)

        # toggle to muted
        client.toggle_mute()
        assert client.muted is True

        # toggle to unmuted
        client.toggle_mute()
        assert client.muted is False

        # the volume should have changed twice
        expected_calls = [mock.call(0), mock.call(volume)]
        assert client_mock.setvol.call_args_list == expected_calls

    def test_context(self, mpdclient):
        client_mock = mpdclient.return_value

        client = single.Client(self.basepath)

        with client:
            pass

        assert client_mock.disconnect.call_count == 1
