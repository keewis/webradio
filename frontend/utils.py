from contextlib import contextmanager
import pathlib
import tempfile


@contextmanager
def basepath(suffix, base='/tmp'):
    try:
        root = pathlib.Path(tempfile.mkdtemp(dir=base))
        yield root / suffix
    finally:
        root.rmdir()
