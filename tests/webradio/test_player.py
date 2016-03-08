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
    def test_playlist(self, mpdclient):
        playlist = [{'a': 1, 'b': 2}, {'a': 3, 'b': 4}]
        socketpath = ""

        mpd = mpdclient.return_value
        mpd.playlistinfo.return_value = playlist
        music_client = player.Player(socketpath)
        assert music_client.playlist == playlist

    @mock.patch("webradio.player.musicpd.MPDClient")
    def test_volume(self, mpdclient):
        volume = 35
        socketpath = ""
        mpd = mpdclient.return_value

        music_client = player.Player(socketpath)

        mpd.status.return_value = {'volume': volume}
        assert music_client.volume == volume

        music_client.volume = 0
        assert mpd.setvol.called_once_with(0)

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

    @mock.patch("webradio.player.musicpd.MPDClient")
    def test_reconnect(self, mpdclient):
        socketpath = ""
        client_mock = mpdclient.return_value

        # without broken pipe
        music_client = player.Player(socketpath)
        client_mock.reset_mock()
        music_client._reconnect()

        expected_calls = [mock.call(port=0, host=socketpath)]

        assert client_mock.disconnect.call_count == 1
        assert client_mock.connect.call_args_list == expected_calls

        # with broken pipe
        music_client = player.Player(socketpath)
        client_mock.reset_mock()
        client_mock.disconnect.side_effect = BrokenPipeError

        music_client._reconnect()

        assert client_mock.disconnect.call_count == 1
        assert client_mock.connect.call_count == 1

    @mock.patch("webradio.player.musicpd.MPDClient")
    def test_ensure_connection_succeeding(self, mpdclient):
        # general set up
        socketpath = ""

        client_mock = mpdclient.return_value
        # succeeding call
        client_mock.ping.return_value = True

        music_client = player.Player(socketpath)
        music_client.clear()
        assert client_mock.disconnect.call_count == 0

    @mock.patch("webradio.player.musicpd.MPDClient")
    def test_ensure_connection_failing(self, mpdclient):
        # general set up
        socketpath = ""

        client_mock = mpdclient.return_value
        # failing call
        client_mock.ping.side_effect = BrokenPipeError

        music_client = player.Player(socketpath)
        music_client.clear()
        assert client_mock.disconnect.call_count == 1
