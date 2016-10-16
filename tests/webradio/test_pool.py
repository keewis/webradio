from unittest import mock
import pytest
import pathlib

import webradio.pool as pool


@pytest.fixture(scope='function')
def single_server():
    m = mock.patch(
        'webradio.pool.single.Server',
        mock.create_autospec(pool.single.Server),
        )

    with m as server:
        yield server


@pytest.fixture(scope='function')
def single_client():
    m = mock.patch(
        'webradio.pool.single.Client',
        mock.create_autospec(pool.single.Client),
        )

    with m as client:
        yield client


@pytest.fixture(scope='function')
def pool_server():
    m = mock.patch(
        'webradio.pool.Server',
        mock.create_autospec(pool.Server),
        )

    with m as server:
        yield server


@pytest.fixture(scope='function')
def pool_client():
    m = mock.patch(
        'webradio.pool.Client',
        mock.create_autospec(pool.Client),
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
    def test_init(self, single_server, path):
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
        assert single_server.call_count == n_instances

    def test_shutdown(self, single_server, path):
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

        assert single_server.return_value.shutdown.call_count == n_instances
        assert basepath.rmdir.call_count == 1

        # raising an OSError
        # construct the server pool
        basepath.exists.return_value = False
        basepath.rmdir.side_effect = OSError
        s = pool.Server(basepath=basepath, num=n_instances)

        # shut it down
        s.shutdown()

    def test_sockets(self, single_server, path):
        basepath = "/pool"
        n_instances = 10
        expected_socket_paths = list(map(str, range(n_instances)))

        basepath = path.return_value
        server_prototype = single_server.return_value
        type(server_prototype).socket = mock.PropertyMock(
            side_effect=expected_socket_paths,
            )

        # construct the server pool
        basepath.exists.return_value = False
        s = pool.Server(basepath=basepath, num=n_instances)

        socket_paths = list(s.sockets)
        assert socket_paths == expected_socket_paths


class TestClient(object):
    def test_init(self, single_client, pool_server):
        n_instances = 10

        server_instance = pool_server.return_value
        type(server_instance).sockets = mock.PropertyMock(
            return_value=range(n_instances),
            )
        muted = mock.PropertyMock()
        type(single_client.return_value).muted = muted

        pool.Client(server_instance)

        # single client construction
        calls = list(
            call[1]['server']
            for call in single_client.call_args_list
            )
        assert calls == list(range(n_instances))

        # single client muted state
        assert muted.call_args_list == [mock.call(True)] * n_instances

    def test_volume(self, single_client, pool_server):
        n_instances = 10
        volume1 = 30
        volume2 = 45

        server_instance = pool_server.return_value
        client_instance = single_client.return_value
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

    def test_urls(self, single_client, pool_server):
        n_instances = 20
        urls1 = tuple(map(str, range(n_instances)))
        urls2 = tuple(map(lambda x: 'x' + str(x), range(n_instances)))

        client_instance = single_client.return_value
        server_instance = pool_server.return_value
        type(server_instance).sockets = mock.PropertyMock(
            return_value=range(n_instances),
            )

        # reading the urls
        url_property = mock.PropertyMock(
            side_effect=[[_] for _ in urls1],
            )
        type(client_instance).urls = url_property

        instance = pool.Client(server_instance)
        assert instance.urls == urls1

        # setting the urls
        url_property = mock.PropertyMock()
        type(client_instance).urls = url_property

        instance.urls = urls2
        assert url_property.call_args_list == [mock.call([_]) for _ in urls2]

        # setting with an invalid number of urls
        with pytest.raises(ValueError) as e:
            instance.urls = list(map(str, range(n_instances + 10)))

        assert "number of urls" in str(e.value)

    def test_muted(self, single_client, pool_server):
        n_instances = 15
        client_instance = single_client.return_value
        server_instance = pool_server.return_value

        type(server_instance).sockets = mock.PropertyMock(
            return_value=range(n_instances),
            )

        instance = pool.Client(server_instance)

        muted = mock.PropertyMock(
            side_effect=[True] * (n_instances - 1) + [False],
            )
        type(client_instance).muted = muted

        # not playing
        # reading
        assert instance.muted is True
        # setting
        instance.muted = True
        assert muted.call_count == 0

        # playing (at least, we pretend to be playing)
        # reading
        instance._current = client_instance
        assert instance.muted is False
        assert muted.call_count == n_instances

        muted.reset_mock()
        # from unmuted to muted
        muted.side_effect = None
        instance.muted = True
        assert muted.call_args_list == [mock.call(True)]

        muted.reset_mock()
        # from muted to unmuted
        instance.muted = False
        assert muted.call_args_list == [mock.call(False)]

    def test_play(self, single_client, pool_server):
        muted = mock.PropertyMock()

        def with_name(value):
            obj = mock.Mock(name=str(value))
            type(obj).muted = muted
            return obj

        n_instances = 13
        index1 = 7
        index2 = 12

        single_client.side_effect = list(map(with_name, range(n_instances)))
        server_instance = pool_server.return_value

        type(server_instance).sockets = mock.PropertyMock(
            return_value=range(n_instances),
            )

        instance = pool.Client(server_instance)
        # delete the muted calls on startup
        muted.reset_mock()

        # play with an index to big: no-op
        with pytest.raises(IndexError):
            instance.play(n_instances + 5)

        assert instance._current is None
        assert muted.call_count == 0

        # with an arbitrary index
        instance.play(index1)
        assert instance._current._mock_name == str(index1)
        calls = [mock.call(True)] * n_instances + [mock.call(False)]
        assert muted.call_args_list == calls

        muted.reset_mock()
        # with another one
        instance.play(index2)
        assert instance._current._mock_name == str(index2)
        assert muted.call_args_list == calls

    def test_mute_functions(self, single_client, pool_server):
        n_instances = 17
        client_instance = single_client.return_value
        server_instance = pool_server.return_value

        current = mock.Mock()
        muted = mock.PropertyMock()
        type(current).muted = muted

        total_muted = mock.PropertyMock()
        type(client_instance).muted = total_muted

        type(server_instance).sockets = mock.PropertyMock(
            return_value=range(n_instances),
            )

        instance = pool.Client(server_instance)
        instance._current = current

        # mute()
        muted.reset_mock()
        instance.mute()
        assert muted.call_args_list == [mock.call(True)]

        # unmute()
        muted.reset_mock()
        instance.unmute()
        assert muted.call_args_list == [mock.call(False)]

        # toggle_mute()
        muted.reset_mock()
        total_muted.side_effect = [True] * n_instances
        instance.toggle_mute()
        assert muted.call_args_list == [mock.call(False)]

        muted.reset_mock()
        total_muted.side_effect = [True] * (n_instances - 1) + [False]
        instance.toggle_mute()
        assert muted.call_args_list == [mock.call(True)]

    def test_context(self, single_client, pool_server):
        n_instances = 10
        client_instance = single_client.return_value
        server_instance = pool_server.return_value

        type(server_instance).sockets = mock.PropertyMock(
            return_value=range(n_instances),
            )

        with pool.Client(server_instance):
            pass

        assert client_instance.disconnect.call_count == n_instances
        assert server_instance.shutdown.call_count == 1


def test_map(pool_client, pool_server):
    client_instance = pool_client.return_value
    server_instance = pool_server.return_value
    basepath = "/music_root"
    n_urls = 10
    urls = list(range(n_urls))

    url_prop = mock.PropertyMock()
    type(client_instance).urls = url_prop

    pool.map(basepath=basepath, urls=urls)

    assert pool_server.call_args_list == [
        mock.call(basepath=basepath, num=n_urls),
        ]
    assert pool_client.call_args_list == [mock.call(server_instance)]
    assert url_prop.call_args_list == [mock.call(urls)]
