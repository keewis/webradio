from contextlib import contextmanager
from functools import partial
import pathlib
import tempfile


prompt = "> "


@contextmanager
def basepath(suffix, base='/tmp'):
    try:
        root = pathlib.Path(tempfile.mkdtemp(dir=base))
        yield root / suffix
    finally:
        root.rmdir()


def format_urls(urls):
    formatted = "\n".join(
        "({}): {}".format(index, url)
        for index, url in enumerate(urls)
        )
    return formatted


def get(dict_, key, default=None):
    for index, proposed_key in enumerate(dict_.keys()):
        if not proposed_key.startswith(key):
            continue
        return dict_[proposed_key]

    return default


def select_action(data, actions):
    command, *args = data.strip().split()
    action = get(actions, command, default=None)

    if action is None:
        raise ValueError()

    processed_args = map(int, args)
    return partial(action, *processed_args)
