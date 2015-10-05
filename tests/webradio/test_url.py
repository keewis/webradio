import sys
from unittest import mock
sys.modules['requests'] = mock.Mock()

import webradio.url as url


def test_urltype():
    test_streams = [
        "http://streams.br.de/bayern2sued_2.m3u",
        "http://streams.br.de/b5aktuell_2.m3u",
        "http://stream-sd.radioparadise.com:8056",
        "http://icecast2.rte.ie/ieradio1",
        ]
    expected_types = [
        "playlist",
        "playlist",
        "direct",
        "direct",
        ]

    types = list(map(url.urltype, test_streams))
    assert types == expected_types


def test_extract_playlist():
    text = (
        "http://br-mp3-bayern2sued-m.akacast.akamaistream.net"
        "/7/731/256282/v1/gnl.akacast.akamaistream.net/br_mp3_bayern2sued_m\n"
        "http://br-mp3-bayern2sued-m.akacast.akamaistream.net"
        "/7/731/256282/v1/gnl.akacast.akamaistream.net/br_mp3_bayern2sued_m\n"
        "http://br-mp3-bayern2sued-s.akacast.akamaistream.net"
        "/7/717/256282/v1/gnl.akacast.akamaistream.net/br_mp3_bayern2sued_s"
        )

    expected_url = (
        "http://br-mp3-bayern2sued-m.akacast.akamaistream.net"
        "/7/731/256282/v1/gnl.akacast.akamaistream.net/br_mp3_bayern2sued_m"
        )
    assert url.extract_playlist(text) == expected_url


def test_acquire_playlist():
    test_url = "http://streams.br.de/bayern2sued_2.m3u"
    expected_content = ""

    get = mock.Mock()
    answer = mock.Mock()
    with mock.patch("requests.get", get):
        get.return_value = answer
        answer.ok = False
        assert url.acquire_playlist(test_url) == expected_content

    answer.reset_mock()
    expected_content = (
        "http://br-mp3-bayern2sued-m.akacast.akamaistream.net"
        "/7/731/256282/v1/gnl.akacast.akamaistream.net/br_mp3_bayern2sued_m\n"
        "http://br-mp3-bayern2sued-m.akacast.akamaistream.net"
        "/7/731/256282/v1/gnl.akacast.akamaistream.net/br_mp3_bayern2sued_m\n"
        "http://br-mp3-bayern2sued-s.akacast.akamaistream.net"
        "/7/717/256282/v1/gnl.akacast.akamaistream.net/br_mp3_bayern2sued_s"
        )
    with mock.patch("requests.get", get):
        answer.ok = True
        answer.text = expected_content
        assert url.acquire_playlist(test_url) == expected_content
