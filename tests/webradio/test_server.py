from unittest import mock
import sys
sys.modules['subprocess'].call = mock.Mock()

import pytest

import webradio.server as server
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

    server.delete(path, recursive=True)
    assert not path.exists()


def test_delete_nonrecursive(tmpdir):
    path = pathlib.Path(tmpdir.strpath) / "test"
    path.mkdir()
    assert path.exists() and path.is_dir()

    server.delete(path, recursive=False)
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
        server.delete(path, recursive=False)
    exception = e.value
    assert exception.errno == errno.ENOTEMPTY


def list_dir(path):
    yield path
    if path.is_dir():
        for p in path.iterdir():
            yield from list_dir(p)


def test_fill_worker_directory(tmpdir):
    path = pathlib.Path(tmpdir.strpath)
    server.fill_worker_directory(path)

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


class TestServerPool(object):
    @mock.patch('webradio.server.subprocess')
    @mock.patch('webradio.server.pathlib.Path')
    def test_init_root_missing(self, path, *args):
        basepath = "pool"
        n_instances = 10

        path_instance = path.return_value
        root_instance = path_instance.parent
        root_instance.exists.return_value = False
        with pytest.raises(FileNotFoundError):
            server.ServerPool(basepath=basepath, num=n_instances)

    @mock.patch('webradio.server.subprocess')
    @mock.patch('webradio.server.pathlib.Path')
    def test_init_basepath_existing(self, path, *args):
        basepath = "pool"
        n_instances = 10

        path_instance = path.return_value
        root_instance = path_instance.parent
        root_instance.exists.return_value = True
        path_instance.exists.return_value = True
        with pytest.raises(FileExistsError):
            server.ServerPool(basepath=basepath, num=n_instances)

    @mock.patch('webradio.server.delete')
    @mock.patch('webradio.server.fill_worker_directory')
    @mock.patch('webradio.server.subprocess.call')
    @mock.patch('webradio.server.pathlib.Path')
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

        pool = server.ServerPool(basepath=basepath, num=n_instances)

        assert len(paths) == n_instances

        subprocess_call_list = [
            mock.call(['/usr/bin/mpd'], env={'XDG_CONFIG_HOME': worker})
            for worker in paths
            ]

        assert subprocess_call.call_args_list == subprocess_call_list
        subprocess_call.reset_mock()
        del pool
        subprocess_call_list = [
            mock.call(['/usr/bin/mpd'], env={'XDG_CONFIG_HOME': worker})
            for worker in paths
            ]
