import testutils
import pytest
from unittest import mock

import frontend.synchronous as synchronous


def test_print_choices(capsys):
    urls = list(map(lambda x: 'x{}'.format(x), range(9)))
    synchronous.print_choices(urls)
    output, _ = capsys.readouterr()

    expected_output = synchronous.utils.format_urls(urls) + "\n"

    assert output == expected_output


def test_print_prompt(capsys):
    synchronous.print_prompt()
    output, _ = capsys.readouterr()

    expected_output = synchronous.utils.prompt

    assert output == expected_output


def test_process_input(fake_client, stdin, capsys):
    urls = list(map(str, range(9)))
    fake_client.urls = urls

    # mute
    with testutils.reset_file(stdin):
        with testutils.print_to_stdin():
            print("mute", flush=True)

        synchronous.process_input(fake_client)
        output, _ = capsys.readouterr()
        assert fake_client.toggle_mute.call_count == 1
        assert output == synchronous.utils.prompt

    # vol
    with testutils.reset_file(stdin):
        new_volume = 10
        with testutils.print_to_stdin():
            print("vol {}".format(new_volume), flush=True)

        synchronous.process_input(fake_client)
        output, _ = capsys.readouterr()
        assert fake_client.volume == new_volume
        assert output == synchronous.utils.prompt

    # station
    with testutils.reset_file(stdin):
        new_channel = 1
        with testutils.print_to_stdin():
            print("play {}".format(new_channel), flush=True)

        synchronous.process_input(fake_client)
        output, _ = capsys.readouterr()
        assert fake_client.play.call_args_list == [mock.call(new_channel)]
        assert output == synchronous.utils.prompt
        fake_client.play.reset_mock()

    # invalid station
    with testutils.reset_file(stdin):
        new_channel = 15
        fake_client.play.side_effect = RuntimeError

        with testutils.print_to_stdin():
            print("play {}".format(new_channel), flush=True)

        synchronous.process_input(fake_client)

        output, _ = capsys.readouterr()
        expected_output = "\n".join([
            synchronous.utils.format_urls(urls),
            synchronous.utils.prompt,
            ])

        assert fake_client.play.call_args_list == [mock.call(new_channel)]
        assert output == expected_output

        fake_client.play.reset_mock()

    # invalid value
    with testutils.reset_file(stdin):
        with testutils.print_to_stdin():
            print("vol19d", flush=True)

        synchronous.process_input(fake_client)
        output, _ = capsys.readouterr()
        expected_output = "\n".join([
            synchronous.utils.format_urls(urls),
            synchronous.utils.prompt,
            ])
        assert output == expected_output

    # help
    with testutils.reset_file(stdin):
        with testutils.print_to_stdin():
            print("help", flush=True)

        synchronous.process_input(fake_client)
        output, _ = capsys.readouterr()
        expected_output = "\n".join([
            synchronous.utils.format_urls(urls),
            synchronous.utils.prompt,
            ])
        assert output == expected_output

    raised = StopIteration

    # empty
    with testutils.reset_file(stdin), pytest.raises(raised):
        synchronous.process_input(fake_client)
        output, _ = capsys.readouterr()
        expected_output = "\n"
        assert output == expected_output

    # EOFError
    with testutils.readline_sideeffect(EOFError), pytest.raises(raised):
        synchronous.process_input(fake_client)
        output, _ = capsys.readouterr()
        assert "\n" == output

    # KeyboardInterrupt
    with testutils.readline_sideeffect(KeyboardInterrupt), \
            pytest.raises(raised):
        synchronous.process_input(fake_client)
        output, _ = capsys.readouterr()
        assert "\n" == output
