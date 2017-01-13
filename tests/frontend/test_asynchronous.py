import asyncio
from contextlib import contextmanager
import io
from unittest import mock

import pytest

import utils
import frontend.asynchronous as asynchronous


@pytest.fixture(scope='function')
def stdin():
    m = mock.patch(
        'sys.stdin',
        new_callable=io.StringIO,
        )

    with m as stdin:
        yield stdin


@pytest.fixture(scope='function')
def client():
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


@contextmanager
def mock_loop():
    old_loop = asyncio.get_event_loop()
    try:
        new_loop = mock.create_autospec(old_loop)
        asyncio.set_event_loop(new_loop)
        yield new_loop
    finally:
        asyncio.set_event_loop(old_loop)


def test_run_loop_forever():
    @asyncio.coroutine
    def long_running(t):
        yield from asyncio.sleep(t)
        raise EOFError()

    @asyncio.coroutine
    def terminating(t):
        yield from asyncio.sleep(t)
        loop = asyncio.get_event_loop()
        loop.stop()

    # once we switch to python 3.5+, async is a keyword
    ensure_future = asyncio.async

    with asynchronous.run_loop_forever():
        ensure_future(long_running(120))
        ensure_future(terminating(0.005))


@pytest.mark.asyncio
def test_print_choices(capsys):
    urls = list(map(lambda x: 'x{}'.format(x), range(9)))
    yield from asynchronous.print_choices(urls)

    formatted_urls = asynchronous.utils.format_urls(urls)
    expected_output = formatted_urls + "\n"

    output, _ = capsys.readouterr()
    assert output == expected_output


@pytest.mark.asyncio
def test_process_input(client, stdin, capsys):
    urls = list(map(str, range(9)))
    client.urls = urls

    # mute
    with utils.reset_file(stdin):
        with utils.print_to_stdin():
            print("mute", flush=True)

        yield from asynchronous.process_input(client)
        output, _ = capsys.readouterr()
        assert client.toggle_mute.call_count == 1
        assert output == asynchronous.utils.prompt

    # vol
    with utils.reset_file(stdin):
        new_volume = 10
        with utils.print_to_stdin():
            print("vol {}".format(new_volume), flush=True)

        yield from asynchronous.process_input(client)
        output, _ = capsys.readouterr()
        assert client.volume == new_volume
        assert output == asynchronous.utils.prompt

    # station
    with utils.reset_file(stdin):
        new_channel = 1
        with utils.print_to_stdin():
            print("{}".format(new_channel), flush=True)

        yield from asynchronous.process_input(client)
        output, _ = capsys.readouterr()
        assert client.play.call_args_list == [mock.call(new_channel)]
        assert output == asynchronous.utils.prompt
        client.play.reset_mock()

    # invalid station
    with utils.reset_file(stdin):
        new_channel = 15
        client.play.side_effect = RuntimeError

        with utils.print_to_stdin():
            print("{}".format(new_channel), flush=True)

        yield from asynchronous.process_input(client)

        output, _ = capsys.readouterr()
        expected_output = "\n".join([
            asynchronous.utils.format_urls(urls),
            asynchronous.utils.prompt,
            ])

        assert client.play.call_args_list == [mock.call(new_channel)]
        assert output == expected_output

        client.play.reset_mock()

    # invalid value
    with utils.reset_file(stdin):
        with utils.print_to_stdin():
            print("vol19d", flush=True)

        yield from asynchronous.process_input(client)
        output, _ = capsys.readouterr()
        expected_output = "\n".join([
            asynchronous.utils.format_urls(urls),
            asynchronous.utils.prompt,
            ])
        assert output == expected_output

    # help
    with utils.reset_file(stdin):
        with utils.print_to_stdin():
            print("help", flush=True)

        yield from asynchronous.process_input(client)
        output, _ = capsys.readouterr()
        expected_output = "\n".join([
            asynchronous.utils.format_urls(urls),
            asynchronous.utils.prompt,
            ])
        assert output == expected_output

    # empty
    with utils.reset_file(stdin):
        yield from asynchronous.process_input(client)
        output, _ = capsys.readouterr()
        expected_output = asynchronous.utils.prompt
        assert output == expected_output

    # EOFError
    with utils.readline_sideeffect(EOFError), mock_loop() as loop:
        yield from asynchronous.process_input(client)
        output, _ = capsys.readouterr()
        assert loop.stop.call_count == 1
        assert "\n" == output

    # KeyboardInterrupt
    with utils.readline_sideeffect(KeyboardInterrupt), mock_loop() as loop:
        yield from asynchronous.process_input(client)
        output, _ = capsys.readouterr()
        assert loop.stop.call_count == 1
        assert "\n" == output
