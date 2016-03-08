import musicpd
from functools import wraps


class Player(object):
    def __init__(self, socketpath):
        self._path = socketpath

        self._client = musicpd.MPDClient()
        self._client.connect(host=socketpath, port=0)

        self.saved_volume = 0

    def _reconnect(self):
        try:
            self._client.disconnect()
        except BrokenPipeError:
            pass

        self._client.connect(host=self._path, port=0)

    def ensure_connection(func):
        @wraps(func)
        def wrapped(self, *args, **kwargs):
            try:
                self._client.ping()
            except BrokenPipeError:
                self._reconnect()

            return func(self, *args, **kwargs)

        return wrapped

    def __del__(self):
        try:
            self._client.disconnect()
        except BrokenPipeError:
            pass

    def clear(self):
        self._client.clear()

    def add(self, url):
        self._client.add(url)

    def play(self, index=None):
        if index is not None:
            self._client.play(index)
        else:
            self._client.play()

    @property
    def volume(self):
        return int(self._client.status().get('volume'))

    @volume.setter
    def volume(self, value):
        self._client.setvol(value)

    def mute(self):
        current_volume = self.volume
        if current_volume == 0:
            return
        self.toggle_mute()

    def unmute(self):
        current_volume = self.volume
        if current_volume != 0:
            return
        self.toggle_mute()

    def toggle_mute(self):
        current_volume = self.volume
        self.volume = self.saved_volume
        self.saved_volume = current_volume

    @property
    def playlist(self):
        return self._client.playlistinfo()
