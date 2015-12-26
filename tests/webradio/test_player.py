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
        client_mock = mpdclient.return_value

        music_client = player.Player(socketpath)
        music_client.play(index)
        client_mock.play.called_once_with(index)

    @mock.patch("webradio.player.musicpd.MPDClient")
    def test_play_plain(self, mpdclient):
        socketpath = ""
        client_mock = mpdclient.return_value

        music_client = player.Player(socketpath)
        music_client.play()

        client_mock.play.call_args_list == [mock.call()]

    @mock.patch("webradio.player.musicpd.MPDClient")
    def test_toggle_mute(self, mpdclient):
        socketpath = ""
        volume = 35

        client_mock = mpdclient.return_value

        music_client = player.Player(socketpath)

        client_mock.status.return_value = {'volume': volume}
        music_client.toggle_mute()

        client_mock.status.return_value = {'volume': 0}
        music_client.toggle_mute()

        expected_calls = [
            mock.call(_)
            for _ in [0, 35]
            ]
        assert client_mock.setvol.call_args_list == expected_calls

    @mock.patch("webradio.player.musicpd.MPDClient")
    def test_mute(self, mpdclient):
        socketpath = ""
        volume = 35

        client_mock = mpdclient.return_value

        music_client = player.Player(socketpath)

        client_mock.status.return_value = {'volume': volume}
        music_client.mute()
        assert client_mock.setvol.called_once_with(0)

        client_mock.setvol.reset_mock()
        client_mock.status.return_value = {'volume': 0}
        music_client.mute()
        assert client_mock.setvol.call_count == 0

    @mock.patch("webradio.player.musicpd.MPDClient")
    def test_unmute(self, mpdclient):
        socketpath = ""
        volume = 35

        client_mock = mpdclient.return_value

        music_client = player.Player(socketpath)

        music_client.saved_volume = volume
        client_mock.status.return_value = {'volume': 0}
        music_client.unmute()
        assert client_mock.setvol.called_once_with(volume)

        client_mock.setvol.reset_mock()
        client_mock.status.return_value = {'volume': volume}
        music_client.unmute()
        assert client_mock.setvol.call_count == 0
