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
        directories = {
            call[1]['basepath']
            for call in server.call_args_list
            }
        # and the number of mkdir calls
        assert directories.pop().mkdir.call_count == n_instances
