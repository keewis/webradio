import functools
import pathlib
import pytest
from unittest import mock

import frontend.utils as utils


@pytest.fixture(scope='function')
def mkdtemp():
    m = mock.patch(
        'frontend.utils.tempfile.mkdtemp',
        mock.create_autospec(utils.tempfile.mkdtemp),
        )

    with m as mkdtemp:
        yield mkdtemp


@pytest.fixture(scope='function')
def partial():
    m = mock.patch(
        'functools.partial',
        mock.create_autospec(functools.partial),
        )

    with m as partial:
        yield partial


def test_basepath(mkdtemp, rmdir):
    base = '/abc'
    suffix = "jkl.mno"

    tmppath = pathlib.Path('/abc/def/ghi')
    mkdtemp.return_value = tmppath

    with utils.basepath(suffix=suffix, base=base) as path:
        assert str(path) == str(tmppath / suffix)

    assert mkdtemp.call_args_list[-1] == mock.call(dir=base)
    assert rmdir.call_args_list[-1] == mock.call(tmppath)


def test_format_urls():
    urls = list(map(lambda x: "x{}".format(x), range(4)))

    expected_format = "\n".join([
        "(0): x0",
        "(1): x1",
        "(2): x2",
        "(3): x3",
        ])

    assert utils.format_urls(urls) == expected_format


def test_get():
    dict_ = {
        'volume': 1,
        'mute': 2,
        'prebuffering': 3,
        }

    # normal cases: full key
    assert 2 == utils.get(dict_, 'mute')
    # abbreviated: the first parts
    assert 1 == utils.get(dict_, 'vol')
    assert 3 == utils.get(dict_, 'pre')
    assert 2 == utils.get(dict_, 'm')

    # something in between: should be invalid
    assert None is utils.get(dict_, 'l', default=None)
    assert False is utils.get(dict_, 'f', default=False)


def test_select_action():
    def set_volume(client, volume):
        pass

    def mute(client):
        pass

    def play(client, index):
        pass

    actions = {
        'volume': set_volume,
        'mute': mute,
        'play': play,
        'help': None,
        }

    # volume
    volume = 20
    action = utils.select_action("volume {}".format(volume), actions)
    assert action.func is set_volume and action.args == tuple([volume])

    # mute
    action = utils.select_action("mute", actions)
    assert action.func is mute and action.args == tuple()

    # play
    index = 5
    action = utils.select_action("play {}".format(index), actions)
    assert action.func is play and action.args == tuple([index])

    # help
    with pytest.raises(ValueError):
        utils.select_action("help", actions)

    # something invalid
    with pytest.raises(ValueError):
        utils.select_action("invalid_command", actions)
