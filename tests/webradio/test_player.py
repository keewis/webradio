from unittest import mock
import pytest

import webradio.player as player


@pytest.fixture(scope='function')
def pool():
    m = mock.patch(
        'webradio.player.pool',
        mock.create_autospec(player.pool),
        )

    with m as pool:
        yield pool


@pytest.fixture(scope='function')
def single():
    m = mock.patch(
        'webradio.player.single',
        mock.create_autospec(player.single),
        )

    with m as single:
        yield single


class TestPlayer(object):
    def test_init_single(self, single, pool):
        n_urls = 11
        basepath = "/webradio"
        urls = list(map(lambda x: "x" + str(x), range(n_urls)))

        client_instance = single.Client.return_value
        url_property = mock.PropertyMock()
        type(client_instance).urls = url_property
        server_instance = single.Server.return_value

        instance = player.Player(
            basepath=basepath,
            urls=urls,
            prebuffering=False,
            )

        assert single.Server.call_args_list == [mock.call(basepath=basepath)]
        assert single.Client.call_args_list == [mock.call(server_instance)]
        assert instance.client is client_instance
        assert instance.server is server_instance
        assert url_property.call_args_list == [mock.call(urls)]

    def test_init_pool(self, single, pool):
        n_urls = 11
        basepath = "/webradio"
        urls = list(map(lambda x: "x" + str(x), range(n_urls)))

        client_instance = pool.Client.return_value
        url_property = mock.PropertyMock()
        type(client_instance).urls = url_property
        server_instance = pool.Server.return_value

        instance = player.Player(
            basepath=basepath,
            urls=urls,
            prebuffering=True,
            )

        assert pool.Server.call_args_list == [
            mock.call(basepath=basepath, num=n_urls)
            ]
        assert pool.Client.call_args_list == [mock.call(server_instance)]
        assert instance.client is client_instance
        assert instance.server is server_instance
        assert url_property.call_args_list == [mock.call(urls)]

    def test_prebuffering(self, single, pool):
        n_urls = 11
        basepath = "/webradio"
        urls = list(map(lambda x: "x" + str(x), range(n_urls)))

        pool_client = pool.Client.return_value
        pool_server = pool.Server.return_value
        single_client = single.Client.return_value
        single_server = single.Server.return_value

        # prebuffering off
        instance = player.Player(
            basepath=basepath,
            urls=urls,
            prebuffering=False,
            )
        assert instance.prebuffering is False
        assert instance.client is single_client
        assert instance.server is single_server

        # off to off: should be a no-op
        instance.prebuffering = False
        assert instance.prebuffering is False
        assert instance.client is single_client
        assert instance.server is single_server

        # off to on
        instance.prebuffering = True
        assert instance.prebuffering is True
        assert instance.client is pool_client
        assert instance.server is pool_server

        # on to on: should be a no-op
        instance.prebuffering = True
        assert instance.prebuffering is True
        assert instance.client is pool_client
        assert instance.server is pool_server

        # on to off
        instance.prebuffering = False
        assert instance.prebuffering is False
        assert instance.client is single_client
        assert instance.server is single_server

    def test_getattr(self, single, pool):
        n_urls = 13
        basepath = "/webradio"
        urls = list(map(lambda x: "x" + str(x), range(n_urls)))
        volume = 34

        single_client = single.Client.return_value
        volume_property = mock.PropertyMock(return_value=volume)
        type(single_client).volume = volume_property

        instance = player.Player(
            basepath=basepath,
            urls=urls,
            prebuffering=False,
            )

        # method passthrough
        index = 10
        instance.play(index)
        assert single_client.play.call_args_list == [mock.call(index)]

        # property reading passthrough
        assert instance.volume == volume
        assert volume_property.call_args_list == [mock.call()]

    def test_setattr(self, single, pool):
        n_urls = 12
        basepath = "/webradio"
        urls = list(map(lambda x: "x" + str(x), range(n_urls)))
        volume = 41

        single_client = single.Client.return_value
        volume_property = mock.PropertyMock(return_value=10)
        type(single_client).volume = volume_property

        instance = player.Player(
            basepath=basepath,
            urls=urls,
            prebuffering=False,
            )

        # property assignment passthrough
        instance.volume = volume
        assert volume_property.call_args_list == [mock.call(volume)]
