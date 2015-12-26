import musicpd


class Player(object):
    def __init__(self, socketpath):
        self._client = musicpd.MPDClient()
        self._client.connect(host=socketpath, port=0)

        self.saved_volume = 0

    def __del__(self):
        self._client.disconnect()

    def clear(self):
        self._client.clear()

    def add(self, url):
        self._client.add(url)

    def play(self, index=None):
        if index is not None:
            self._client.play(index)
        else:
            self._client.play()

    def mute(self):
        current_volume = int(self._client.status().get('volume'))
        if current_volume == 0:
            return
        self.toggle_mute()

    def unmute(self):
        current_volume = int(self._client.status().get('volume'))
        if current_volume != 0:
            return
        self.toggle_mute()

    def toggle_mute(self):
        current_volume = int(self._client.status().get('volume'))
        self._client.setvol(self.saved_volume)
        self.saved_volume = current_volume
