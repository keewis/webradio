import io
import pathlib
import pytest
from unittest import mock


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
