import pathlib

from . import base
from . import single
from .base import ignore


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
            self.basepath / "webradio{}".format(index)
            for index in range(num)
            ]

        self.workers = list(
            single.Server(basepath=directory)
            for directory in worker_directories
            )

    @property
    def sockets(self):
        for worker in self.workers:
            yield worker.socket

    def shutdown(self):
        # don't do anything if we already shut down
        if not self.workers:
            return

        for worker in self.workers:
            worker.shutdown()
        self.workers = []

        with ignore(OSError):
            self.basepath.rmdir()


class Client(base.base_client):
    def __init__(self, server, *, muted=False):
        self.server = server
        self.clients = tuple(
            single.Client(server=path)
            for path in server.sockets
            )
        self._urls = []

        self._current = None
        for client in self.clients:
            client.muted = True

    @property
    def volume(self):
        # if we don't have clients, this will raise an index error
        return self.clients[-1].volume

    @volume.setter
    def volume(self, new_volume):
        for client in self.clients:
            client.volume = new_volume

    @property
    def urls(self):
        pass

    @urls.setter
    def urls(self, urls):
        pass

    def play(self, index):
        pass

    @property
    def muted(self):
        pass

    @muted.setter
    def muted(self, new_state):
        pass

    def mute(self):
        pass

    def unmute(self):
        pass

    def toggle_mute(self):
        pass
