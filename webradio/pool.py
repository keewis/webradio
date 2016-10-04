import pathlib
from . import single
from contextlib import contextmanager


@contextmanager
def ignore(exception):
    try:
        yield
    except exception:
        pass


class Server(object):
    def __init__(self, *, basepath, num):
        self.workers = []

        self.basepath = pathlib.Path(basepath)
        if self.basepath.exists():
            raise FileExistsError(
                "{} does already exist... not overwriting".format(
                    self.basepath,
                    ))

        # create the root dir
        self.basepath.mkdir(mode=0o700)

        # create the worker dirs
        worker_directories = [
            self.basepath / "worker{}".format(index)
            for index in range(num)
            ]
        for worker in worker_directories:
            worker.mkdir(mode=0o700)

        self.workers = list(
            single.Server(basepath=directory)
            for directory in worker_directories
            )

    @property
    def sockets(self):
        for worker in self.workers:
            yield worker.socket

    def shutdown(self):
        for worker in self.workers:
            worker.shutdown()

        with ignore(OSError):
            self.basepath.rmdir()
