from unittest import mock
import sys
sys.modules['subprocess'].call = mock.Mock()

import pytest

import webradio.pool as pool
import pathlib
import errno


class TestServer(object):
    @mock.patch('webradio.pool.subprocess')
    @mock.patch('webradio.pool.pathlib.Path')
    def test_init_root_missing(self, path, *args):
        basepath = "pool"
        n_instances = 10

        path_instance = path.return_value.absolute.return_value
        root_instance = path_instance.parent
        root_instance.exists.return_value = False
        with pytest.raises(FileNotFoundError):
            pool.Server(basepath=basepath, num=n_instances)

    @mock.patch('webradio.pool.subprocess')
    @mock.patch('webradio.pool.pathlib.Path')
    def test_init_basepath_existing(self, path, *args):
        basepath = "pool"
        n_instances = 10

        path_instance = path.return_value.absolute.return_value
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

        path_instance = path.return_value.absolute.return_value
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

    @mock.patch('webradio.pool.delete')
    @mock.patch('webradio.pool.fill_worker_directory')
    @mock.patch('webradio.pool.subprocess.call')
    @mock.patch('webradio.pool.pathlib.Path')
    def test_sockets(self, path, subprocess_call, *args):
        basepath = "pool"
        n_instances = 10

        paths = []

        class fake_path(object):
            def __init__(self, path):
                self.path = path

            def absolute(self):
                return self

            def mkdir(self, mode):
                pass

            def __truediv__(self, path):
                appended_path = "/".join([self.path, path])
                return type(self)(appended_path)

            def __str__(self):
                return self.path

        def path_append(pathname):
            return fake_path(basepath) / pathname

        path_instance = path.return_value.absolute.return_value
        root_instance = path_instance.parent
        root_instance.exists.return_value = True
        path_instance.exists.return_value = False
        path_instance.__truediv__.side_effect = path_append

        server_pool = pool.Server(basepath=basepath, num=n_instances)
        sockets = list(map(str, server_pool.sockets))
        expected_sockets = list(map(
            lambda x: "/".join([
                basepath,
                "worker{}/mpd/socket".format(x),
                ]),
            range(n_instances),
            ))

        assert sockets == expected_sockets
