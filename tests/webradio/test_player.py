import sys
import os.path
from unittest import mock

sys.modules['musicpd'] = mock.Mock()

import webradio.player as player


class TestPlayer(object):
    @mock.patch("webradio.player.musicpd.MPDClient")
    def test_init(self, mpdclient):
        socketpath = os.path.expanduser("~/.config/mpd/socket")
        client_mock = mpdclient()
        music_client = player.Player(socketpath)

        assert isinstance(music_client, player.Player)
        client_mock.connect.called_once_with(host=socketpath, port=0)

    @mock.patch("webradio.player.musicpd.MPDClient")
    def test_destroy(self, mpdclient):
        socketpath = ""
        client_mock = mpdclient()
        player.Player(socketpath)

        assert client_mock.disconnect.call_count == 1

    @mock.patch("webradio.player.musicpd.MPDClient")
    def test_add(self, mpdclient):
        socketpath = ""
        url = "abc"
        client_mock = mpdclient()
        music_client = player.Player(socketpath)

        music_client.add(url)
        assert client_mock.add.call_count == 1

    @mock.patch("webradio.player.musicpd.MPDClient")
    def test_clear(self, mpdclient):
        socketpath = ""
        client_mock = mpdclient()

        music_client = player.Player(socketpath)
        music_client.clear()
        assert client_mock.clear.call_count == 1

    @mock.patch("webradio.player.musicpd.MPDClient")
    def test_play(self, mpdclient):
        socketpath = ""
        index = 5
        client_mock = mpdclient()

        music_client = player.Player(socketpath)
        music_client.play(index)
        client_mock.play.called_once_with(index)
