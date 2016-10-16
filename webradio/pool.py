import pathlib
import itertools

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
        return tuple(itertools.chain.from_iterable(
            client.urls for client in self.clients
            ))

    @urls.setter
    def urls(self, urls):
        if len(urls) != len(self.clients):
            raise ValueError("number of urls != number of clients")

        self._urls = urls

        for url, client in zip(urls, self.clients):
            client.clear()
            client.urls = [url]
            client.play()
            client.muted = True

    def play(self, index):
        self._current = self.clients[index]

        for client in self.clients:
            client.muted = True
        self._current.muted = False

    @property
    def muted(self):
        if self._current is None:
            return True

        return all(client.muted for client in self.clients)

    @muted.setter
    def muted(self, new_state):
        if self._current is None:
            return

        self._current.muted = new_state

    def mute(self):
        self.muted = True

    def unmute(self):
        self.muted = False

    def toggle_mute(self):
        self.muted = not self.muted

    def __enter__(self):
        return self

    def __exit__(self, cls, exception, traceback):
        for client in self.clients:
            client.disconnect()

        self.server.shutdown()
