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
def client():
    m = mock.patch(
        'webradio.pool.single.Client',
        mock.create_autospec(pool.single.Client),
        )

    with m as client:
        yield client


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


class TestClient(object):
    def test_init(self, client, server):
        n_instances = 10

        server_instance = server.return_value
        type(server_instance).sockets = mock.PropertyMock(
            return_value=range(n_instances),
            )
        muted = mock.PropertyMock()
        type(client.return_value).muted = muted

        pool.Client(server_instance)

        # single client construction
        calls = list(
            call[1]['server']
            for call in client.call_args_list
            )
        assert calls == list(range(n_instances))

        # single client muted state
        assert muted.call_args_list == [mock.call(True)] * n_instances

    def test_volume(self, client, server):
        n_instances = 10
        volume1 = 30
        volume2 = 45

        server_instance = server.return_value
        client_instance = client.return_value
        type(server_instance).sockets = mock.PropertyMock(
            return_value=range(n_instances),
            )
        volume = mock.PropertyMock(
            return_value=volume1,
            )
        type(client_instance).volume = volume

        instance = pool.Client(server_instance)

        # check initial pass through
        assert instance.volume == volume1
        volume.reset_mock()

        # check pass through by setting
        instance.volume = volume2
        assert volume.call_args_list == [mock.call(volume2)] * n_instances
