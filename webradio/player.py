import musicpd


class Player(object):
    def __init__(self, socketpath):
        self._client = musicpd.MPDClient()
        self._client.connect(host=socketpath, port=0)
