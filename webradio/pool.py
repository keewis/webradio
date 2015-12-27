import pathlib
import subprocess
from . import player


def delete(path, recursive=False):
    if recursive and path.is_dir():
        for item in path.iterdir():
            delete(item, recursive=recursive)

    if path.is_dir():
        path.rmdir()
    else:
        path.unlink()


config_template = """
music_directory    "~/Music"
playlist_directory "{base}/mpd/playlists"
db_file            "{base}/mpd/database"
log_file           "{base}/mpd/log"
pid_file           "{base}/mpd/pid"
state_file         "{base}/mpd/state"
sticker_file       "{base}/mpd/sticker.sql"

bind_to_address    "{base}/mpd/socket"

input {{
    plugin "curl"
}}

audio_output {{
    type        "alsa"
    name        "internal speakers"
    mixer_type  "software"
}}

replaygain    "off"
"""


def fill_worker_directory(path):
    mpdpath = path / "mpd"
    mpdpath.mkdir(mode=0o700)
    (mpdpath / "playlists").mkdir(mode=0o700)
    (mpdpath / "database").touch()
    with (mpdpath / "mpd.conf").open('w') as f:
        f.write(config_template.format(base=str(path.absolute())))


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
        self.workers = [
            self.basepath / "worker{}".format(index)
            for index in range(num)
            ]
        for worker in self.workers:
            worker.mkdir(mode=0o700)
            fill_worker_directory(worker)
            subprocess.call(
                ["/usr/bin/mpd"],
                env={'XDG_CONFIG_HOME': str(worker.absolute())},
                )

    def __del__(self):
        for worker in self.workers:
            subprocess.call(
                ['/usr/bin/mpd', '--kill'],
                env={'XDG_CONFIG_HOME': str(worker.absolute())},
                )
        delete(self.basepath, recursive=True)


class Client(object):
    def __init__(self, server, *, volume=50):
        self.server = server
        self.players = tuple(
            player.Player(str(path))
            for path in server.workers
            )

        for client in self.players:
            client.volume = volume

    def set(self, urls):
        if len(urls) != len(self.players):
            raise RuntimeError(
                "number of passed urls ({}) does"
                " not match the number of players ({})".format(
                    len(urls),
                    len(self.players),
                    ))

        for url, client in zip(urls, self.players):
            client.clear()
            client.add(url)
            client.play()
            client.mute()

    def play(self, index):
        try:
            playlist = self.players[index].playlist
        except IndexError:
            raise RuntimeError("invalid index")

        if len(playlist) == 0:
            raise RuntimeError("playlist is empty")

        for client in self.players:
            client.mute()

        self.players[index].unmute()

    def __del__(self):
        for client in self.players:
            client.mute()
        del self.server
