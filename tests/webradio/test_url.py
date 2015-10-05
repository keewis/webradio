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
