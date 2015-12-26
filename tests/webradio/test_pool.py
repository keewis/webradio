from unittest import mock
import sys
sys.modules['subprocess'].call = mock.Mock()

import pytest

import webradio.pool as pool
import pathlib
import errno


def test_delete_recursive(tmpdir):
    path = pathlib.Path(tmpdir.strpath) / "test"
    path.mkdir()
    assert path.exists() and path.is_dir()

    for i in range(10):
        subdir = path / "sub{}".format(i)
        subdir.mkdir()
        assert subdir.exists() and subdir.is_dir()
        for j in range(20):
            cfile = subdir / "file{}".format(j)
            cfile.touch()
            assert cfile.exists() and cfile.is_file()

    pool.delete(path, recursive=True)
    assert not path.exists()


def test_delete_nonrecursive(tmpdir):
    path = pathlib.Path(tmpdir.strpath) / "test"
    path.mkdir()
    assert path.exists() and path.is_dir()

    pool.delete(path, recursive=False)
    assert not path.exists()


def test_delete_nonrecursive_filled(tmpdir):
    path = pathlib.Path(tmpdir.strpath) / "test"
    path.mkdir()
    assert path.exists() and path.is_dir()
    for i in range(10):
        cfile = path / "file{}".format(i)
        cfile.touch()
        assert cfile.exists() and cfile.is_file()

    with pytest.raises(OSError) as e:
        pool.delete(path, recursive=False)
    exception = e.value
    assert exception.errno == errno.ENOTEMPTY


def list_dir(path):
    yield path
    if path.is_dir():
        for p in path.iterdir():
            yield from list_dir(p)


def test_fill_worker_directory(tmpdir):
    path = pathlib.Path(tmpdir.strpath)
    pool.fill_worker_directory(path)

    raw_content = list(
        p.relative_to(path)
        for p in list_dir(path)
        )
    content = sorted(
        p
        for p in raw_content
        if str(p) != '.'
        )

    expected_content = ['mpd', 'mpd/database', 'mpd/mpd.conf', 'mpd/playlists']
    assert list(map(str, content)) == expected_content
    config_path = path / "mpd" / "mpd.conf"
    size = config_path.stat().st_size
    assert config_path.is_file() and size > 0


class TestServer(object):
    @mock.patch('webradio.pool.subprocess')
    @mock.patch('webradio.pool.pathlib.Path')
    def test_init_root_missing(self, path, *args):
        basepath = "pool"
        n_instances = 10

        path_instance = path.return_value
        root_instance = path_instance.parent
        root_instance.exists.return_value = False
        with pytest.raises(FileNotFoundError):
            pool.Server(basepath=basepath, num=n_instances)

    @mock.patch('webradio.pool.subprocess')
    @mock.patch('webradio.pool.pathlib.Path')
    def test_init_basepath_existing(self, path, *args):
        basepath = "pool"
        n_instances = 10

        path_instance = path.return_value
        root_instance = path_instance.parent
        root_instance.exists.return_value = True
        path_instance.exists.return_value = True
        with pytest.raises(FileExistsError):
            pool.Server(basepath=basepath, num=n_instances)

    @mock.patch('webradio.pool.delete')
    @mock.patch('webradio.pool.fill_worker_directory')
    @mock.patch('webradio.pool.subprocess.call')
    @mock.patch('webradio.pool.pathlib.Path')
    def test_init(self, path, subprocess_call, *args):
        basepath = "pool"
        n_instances = 10

        paths = []

        def path_append(pathname):
            full_path = "/".join([
                basepath,
                pathname,
                ])
            paths.append(full_path)
            m = mock.Mock(name=full_path)
            m.absolute.return_value = full_path
            return m

        path_instance = path.return_value
        root_instance = path_instance.parent
        root_instance.exists.return_value = True
        path_instance.exists.return_value = False
        path_instance.__truediv__.side_effect = path_append

        server_pool = pool.Server(basepath=basepath, num=n_instances)

        assert len(paths) == n_instances

        subprocess_call_list = [
            mock.call(['/usr/bin/mpd'], env={'XDG_CONFIG_HOME': worker})
            for worker in paths
            ]

        assert subprocess_call.call_args_list == subprocess_call_list
        subprocess_call.reset_mock()
        del server_pool
        subprocess_call_list = [
            mock.call(['/usr/bin/mpd'], env={'XDG_CONFIG_HOME': worker})
            for worker in paths
            ]


class TestClient(object):
    @mock.patch("webradio.player.Player")
    def test_init_single(self, player):
        path = "abc"
        client_pool = pool.Client(path)
        assert len(client_pool.players) == 1
        assert player.call_args_list == [mock.call(path)]

    @mock.patch("webradio.player.Player")
    def test_init(self, player):
        paths = [
            "worker{}".format(_)
            for _ in range(10)
            ]

        player_instance = player.return_value

        volume_mock = mock.PropertyMock(return_value=40)
        with player_instance:
            type(player_instance).volume = volume_mock

            client_pool = pool.Client(paths)

            assert len(client_pool.players) == len(paths)
            expected_calls = [
                mock.call(path)
                for path in paths
                ]
            assert player.call_args_list == expected_calls
            expected_calls = [mock.call(50)] * len(paths)
            assert volume_mock.call_args_list == expected_calls

        volume = 60
        volume_mock = mock.PropertyMock(return_value=40)
        with player_instance:
            type(player_instance).volume = volume_mock

            client_pool = pool.Client(paths, volume=volume)
            assert len(client_pool.players) == len(paths)

            expected_calls = [mock.call(volume)] * len(paths)
            assert volume_mock.call_args_list == expected_calls

    @mock.patch("webradio.player.Player")
    def test_del(self, player):
        paths = ["worker{}".format(_) for _ in range(10)]

        player_instance = player.return_value
        client_pool = pool.Client(paths)
        del client_pool

        assert player_instance.mute.call_count == len(paths)

    @mock.patch("webradio.player.Player")
    def test_set(self, player):
        paths = ["worker0", "worker1"]
        urls = ["url1", "url2"]

        player_instance = player.return_value
        client_pool = pool.Client(paths)

        client_pool.set(urls)

        assert player_instance.clear.call_count == len(urls)
        assert player_instance.mute.call_count == len(urls)
        expected_calls = list(map(mock.call, urls))
        assert player_instance.add.call_args_list == expected_calls

    @mock.patch("webradio.player.Player")
    def test_play_invalid(self, player):
        paths = list(map(str, range(10)))
        urls = list(map(str, range(1, 11)))

        client_pool = pool.Client(paths)

        with pytest.raises(RuntimeError):
            client_pool.play(5)

        client_pool.set(urls)

        with pytest.raises(RuntimeError):
            client_pool.play(10)

    @mock.patch("webradio.player.Player")
    def test_play(self, player):
        paths = list(map(str, range(10)))
        urls = list(map(str, range(1, 11)))
        index = 5

        player_mocks = [
            mock.Mock(name="Player('{}')".format(_))
            for _ in paths
            ]
        for player_mock, url in zip(player_mocks, urls):
            player_mock.playlist = [url]

        player.side_effect = player_mocks

        client_pool = pool.Client(paths)
        client_pool.set(urls)

        mute_call_counts = [
            m.mute.call_count
            for m in player_mocks
            ]
        assert mute_call_counts == [1] * len(urls)

        for m in player_mocks:
            m.mute.reset_mock()

        client_pool.play(index)

        mute_call_counts = [
            m.mute.call_count
            for m in player_mocks
            ]
        assert mute_call_counts == [1] * len(urls)
        assert player_mocks[index].unmute.call_count == 1
