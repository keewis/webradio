import asyncio
from contextlib import contextmanager
from unittest import mock

import pytest

import testutils
import frontend.asynchronous as asynchronous


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
def test_process_input(fake_client, stdin, capsys):
    urls = list(map(str, range(9)))
    fake_client.urls = urls

    # mute
    with testutils.reset_file(stdin):
        with testutils.print_to_stdin():
            print("mute", flush=True)

        yield from asynchronous.process_input(fake_client)
        output, _ = capsys.readouterr()
        assert fake_client.toggle_mute.call_count == 1
        assert output == asynchronous.utils.prompt

    # vol
    with testutils.reset_file(stdin):
        new_volume = 10
        with testutils.print_to_stdin():
            print("vol {}".format(new_volume), flush=True)

        yield from asynchronous.process_input(fake_client)
        output, _ = capsys.readouterr()
        assert fake_client.volume == new_volume
        assert output == asynchronous.utils.prompt

    # station
    with testutils.reset_file(stdin):
        new_channel = 1
        with testutils.print_to_stdin():
            print("play {}".format(new_channel), flush=True)

        yield from asynchronous.process_input(fake_client)
        output, _ = capsys.readouterr()
        assert fake_client.play.call_args_list == [mock.call(new_channel)]
        assert output == asynchronous.utils.prompt
        fake_client.play.reset_mock()

    # invalid station
    with testutils.reset_file(stdin):
        new_channel = 15
        fake_client.play.side_effect = RuntimeError

        with testutils.print_to_stdin():
            print("play {}".format(new_channel), flush=True)

        yield from asynchronous.process_input(fake_client)

        output, _ = capsys.readouterr()
        expected_output = "\n".join([
            asynchronous.utils.format_urls(urls),
            asynchronous.utils.prompt,
            ])

        assert fake_client.play.call_args_list == [mock.call(new_channel)]
        assert output == expected_output

        fake_client.play.reset_mock()

    # invalid value
    with testutils.reset_file(stdin):
        with testutils.print_to_stdin():
            print("vol19d", flush=True)

        yield from asynchronous.process_input(fake_client)
        output, _ = capsys.readouterr()
        expected_output = "\n".join([
            asynchronous.utils.format_urls(urls),
            asynchronous.utils.prompt,
            ])
        assert output == expected_output

    # help
    with testutils.reset_file(stdin):
        with testutils.print_to_stdin():
            print("help", flush=True)

        yield from asynchronous.process_input(fake_client)
        output, _ = capsys.readouterr()
        expected_output = "\n".join([
            asynchronous.utils.format_urls(urls),
            asynchronous.utils.prompt,
            ])
        assert output == expected_output

    # empty
    with testutils.reset_file(stdin):
        yield from asynchronous.process_input(fake_client)
        output, _ = capsys.readouterr()
        expected_output = "\n"
        assert output == expected_output

    # EOFError
    with testutils.readline_sideeffect(EOFError), mock_loop() as loop:
        yield from asynchronous.process_input(fake_client)
        output, _ = capsys.readouterr()
        assert loop.stop.call_count == 1
        assert "\n" == output

    # KeyboardInterrupt
    with testutils.readline_sideeffect(KeyboardInterrupt), mock_loop() as loop:
        yield from asynchronous.process_input(fake_client)
        output, _ = capsys.readouterr()
        assert loop.stop.call_count == 1
        assert "\n" == output
