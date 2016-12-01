from contextlib import contextmanager
import pathlib
import tempfile


@contextmanager
def basepath(suffix):
    try:
        root = pathlib.Path(tempfile.mkdtemp(dir='/tmp'))
        yield root / suffix
    finally:
        root.rmdir()
