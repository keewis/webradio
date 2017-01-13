import io
import pathlib
import pytest
from unittest import mock

import webradio


@pytest.fixture(scope='function')
def rmdir():
    m = mock.patch(
        'pathlib.Path.rmdir',
        mock.create_autospec(pathlib.Path.rmdir),
        )

    with m as rmdir:
        yield rmdir


@pytest.fixture(scope='function')
def stdin():
    m = mock.patch(
        'sys.stdin',
        new_callable=io.StringIO,
        )

    with m as stdin:
        yield stdin


@pytest.fixture(scope='function')
def fake_client():
    m = mock.Mock(
        name='fake_client',
        spec=[
            'volume',
            'toggle_mute',
            'play',
            'urls',
            ],
        )
    yield m


@pytest.fixture(scope='function')
def single_server():
    m = mock.patch(
        'webradio.single.Server',
        mock.create_autospec(webradio.single.Server),
        )

    with m as server:
        yield server


@pytest.fixture(scope='function')
def single_client():
    m = mock.patch(
        'webradio.single.Client',
        mock.create_autospec(webradio.single.Client),
        )

    with m as client:
        yield client
