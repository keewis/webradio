import sys
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
