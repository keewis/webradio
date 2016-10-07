from unittest import mock
import pytest
import pathlib

import webradio.pool as pool


@pytest.fixture(scope='function')
def server():
    m = mock.patch(
        'webradio.pool.single.Server',
        mock.create_autospec(pool.single.Server),
        )

    with m as server:
        yield server


@pytest.fixture(scope='function')
def path():
    m = mock.patch(
        'webradio.pool.pathlib.Path',
        mock.create_autospec(pathlib.Path),
        )

    with m as path:
        yield path


class TestServer(object):
    def test_init(self, server, path):
        basepath = "/pool"
        n_instances = 10

        basepath = path.return_value

        # basepath exists
        basepath.exists.return_value = True
        with pytest.raises(FileExistsError):
            pool.Server(basepath=basepath, num=n_instances)

        # succeeding
        basepath.exists.return_value = False
        pool.Server(basepath=basepath, num=n_instances)

        # check the number of server calls
        assert server.call_count == n_instances

    def test_shutdown(self, server, path):
        basepath = "/pool"
        n_instances = 10

        basepath = path.return_value

        # succeeding
        # construct the server pool
        basepath.exists.return_value = False
        s = pool.Server(basepath=basepath, num=n_instances)

        # shut it down
        s.shutdown()

        # shut it down a second time (which should be a no-op)
        s.shutdown()

        assert server.return_value.shutdown.call_count == n_instances
        assert basepath.rmdir.call_count == 1

        # raising an OSError
        # construct the server pool
        basepath.exists.return_value = False
        basepath.rmdir.side_effect = OSError
        s = pool.Server(basepath=basepath, num=n_instances)

        # shut it down
        s.shutdown()

    def test_sockets(self, server, path):
        basepath = "/pool"
        n_instances = 10
        expected_socket_paths = list(map(str, range(n_instances)))

        basepath = path.return_value
        server_prototype = server.return_value
        type(server_prototype).socket = mock.PropertyMock(
            side_effect=expected_socket_paths,
            )

        # construct the server pool
        basepath.exists.return_value = False
        s = pool.Server(basepath=basepath, num=n_instances)

        socket_paths = list(s.sockets)
        assert socket_paths == expected_socket_paths
