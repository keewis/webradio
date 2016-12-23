from contextlib import contextmanager
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


def format_choices(urls):
    formatted = "\n".join(
        "({}): {}".format(index, url)
        for index, url in enumerate(urls)
        )
    return formatted
