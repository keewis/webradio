import pathlib
from . import single


class Server(object):
    def __init__(self, *, basepath, num):
        self.workers = []

        self.basepath = pathlib.Path(basepath).absolute()
        root = self.basepath.parent
        if not root.exists():
            raise FileNotFoundError("{} does not exist".format(root))

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

        try:
            self.basepath.rmdir()
        except OSError:
            pass
