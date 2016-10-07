from functools import wraps
import pathlib
import shutil
import subprocess

import musicpd

from . import base
from .base import ignore


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


def fill(path):
    mpdpath = path / "mpd"
    mpdpath.mkdir(mode=0o700)
    (mpdpath / "playlists").mkdir(mode=0o700)
    (mpdpath / "database").touch()
    with (mpdpath / "mpd.conf").open('w') as f:
        f.write(config_template.format(base=str(path.absolute())))


class Server(object):
    def __init__(self, *, basepath):
        self.basepath = pathlib.Path(basepath).absolute()

        if self.basepath.exists():
            raise FileExistsError(
                "{} does already exist... not overwriting".format(
                    self.basepath,
                    ))

        self.basepath.mkdir(mode=0o700)

        fill(self.basepath)
        subprocess.call(
            ["/usr/bin/mpd"],
            env={'XDG_CONFIG_HOME': str(self.basepath.absolute())},
            )

    @property
    def socket(self):
        return self.basepath / "mpd" / "socket"

    def shutdown(self):
        mpd = self.basepath / "mpd"
        if mpd.exists():
            subprocess.call(
                ['/usr/bin/mpd', '--kill'],
                env={'XDG_CONFIG_HOME': str(self.basepath.absolute())},
                )

        with ignore((FileNotFoundError, OSError)):
            # only remove the mpd subtree using something like rm -rf
            shutil.rmtree(str(mpd.absolute()))

            # try to remove the basepath (if it's empty)
            self.basepath.rmdir()


class Client(base.base_client):
    def __init__(self, server, *, muted=False):
        try:
            self.basepath = server.socket
            self.server = server
        except AttributeError:
            self.basepath = pathlib.Path(server).absolute()
            self.server = None

        self._client = musicpd.MPDClient()
        self._connect()

        self._muted = muted
        self._volume = self._get_volume()

        self._urls = []

    def __enter__(self):
        return self

    def __exit__(self, cls, exception, traceback):
        self.disconnect()

        with ignore(AttributeError):
            self.server.shutdown()

    def ensure_connection(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            try:
                self._client.ping()
            except BrokenPipeError:
                self._reconnect()

            return func(self, *args, **kwargs)

        return wrapper

    def _reconnect(self):
        self.disconnect()
        self._connect()

    def disconnect(self):
        with ignore(BrokenPipeError):
            self._client.disconnect()

    def _connect(self):
        self._client.connect(host=str(self.basepath), port=0)

    @ensure_connection
    def _get_volume(self):
        return int(self._client.status().get('volume'))

    @ensure_connection
    def _set_volume(self, new_volume):
        self._client.setvol(new_volume)

    @property
    def volume(self):
        return self._volume

    @volume.setter
    def volume(self, new_volume):
        if not self.muted:
            self._set_volume(int(new_volume))

        self._volume = int(new_volume)

    @property
    def urls(self):
        return self._urls

    @urls.setter
    def urls(self, urls):
        self.clear()
        for url in urls:
            self.add(url)

    @ensure_connection
    def add(self, url):
        self._client.add(url)
        self._urls.append(url)

    @ensure_connection
    def clear(self):
        self._client.clear()
        self._urls = []

    @ensure_connection
    def play(self, index=None):
        if index is None:
            self._client.play()
        else:
            if index >= len(self._urls):
                raise RuntimeError("invalid song index")
            self._client.play(index)

    @property
    def muted(self):
        return self._muted

    @muted.setter
    def muted(self, new_state):
        if self._muted == new_state:
            # if the required new state is the current one
            return

        self._muted = bool(new_state)
        self._set_volume(0 if self._muted else self._volume)

    def mute(self):
        self.muted = True

    def unmute(self):
        self.muted = False

    def toggle_mute(self):
        self.muted = not self.muted
