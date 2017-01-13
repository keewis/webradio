from contextlib import contextmanager, redirect_stdout
import io
import sys
from unittest import mock


@contextmanager
def readline_sideeffect(exception):
    m = mock.patch(
        'sys.stdin.readline',
        new_callable=mock.Mock,
        )
    with m as readline:
        try:
            readline.side_effect = exception
            yield readline
        finally:
            readline.side_effect = None


@contextmanager
def print_to_stdin():
    stdout = io.StringIO()
    with redirect_stdout(stdout):
        yield
    sys.stdin.write(stdout.getvalue())
    sys.stdin.seek(0)


@contextmanager
def reset_file(filelike):
    try:
        yield
    finally:
        filelike.truncate(0)
        filelike.seek(0)
