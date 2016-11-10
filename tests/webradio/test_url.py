import pytest
from unittest import mock

import webradio.url as url


@pytest.fixture(scope='function')
def requests():
    m = mock.patch(
        'webradio.url.requests',
        mock.create_autospec(url.requests)
        )

    with m as requests:
        yield requests


@pytest.fixture(scope='function')
def urltype():
    m = mock.patch(
        'webradio.url.urltype',
        mock.create_autospec(url.urltype),
        )

    with m as urltype:
        yield urltype


@pytest.fixture(scope='function')
def acquire_playlist():
    m = mock.patch(
        'webradio.url.acquire_playlist',
        mock.create_autospec(url.acquire_playlist),
        )

    with m as acquire_playlist:
        yield acquire_playlist


@pytest.fixture(scope='function')
def extract_playlist():
    m = mock.patch(
        'webradio.url.extract_playlist',
        mock.create_autospec(url.extract_playlist),
        )

    with m as extract_playlist:
        yield extract_playlist


urls = (
    "http://www.m2radio.fr/pls/m2purple_winamp.m3u",
    "http://players.creacast.com/creacast/accent4/playlist.pls",
    "http://streaming.hotmixradio.fm/hotmixradio-80-128.mp3",
    "http://stream-sd.radioparadise.com:8056",
    "http://icecast2.rte.ie/ieradio1",
    )
url_types = (
    "m3u",
    "pls",
    "direct",
    "direct",
    "direct",
)
content = (
    "http://br-mp3-bayern2sued-m.akacast.akamaistream.net"
    "/7/731/256282/v1/gnl.akacast.akamaistream.net/br_mp3_bayern2sued_m\n"
    "http://br-mp3-bayern2sued-m.akacast.akamaistream.net"
    "/7/731/256282/v1/gnl.akacast.akamaistream.net/br_mp3_bayern2sued_m\n"
    "http://br-mp3-bayern2sued-s.akacast.akamaistream.net"
    "/7/717/256282/v1/gnl.akacast.akamaistream.net/br_mp3_bayern2sued_s"
    )
extracted_url = (
    "http://br-mp3-bayern2sued-m.akacast.akamaistream.net"
    "/7/731/256282/v1/gnl.akacast.akamaistream.net/br_mp3_bayern2sued_m"
    )
prepared_urls = tuple(
    url if index != 0 else extracted_url
    for index, url in enumerate(urls)
    )


def test_urltype():
    types = tuple(map(url.urltype, urls))
    assert types == url_types


def test_parse_m3u():
    content = "\n".join([
        "#EXTM3U",
        (
            "#EXTINF:-1,H o t M i x R a d i o"
            " - Hotmixradio 80 - http://www.hotmixradio.fr"
            ),
        "http://streaming.hotmixradio.fm/hotmixradio-80-128.mp3",
        (
            "#EXTINF:-1,H o t M i x R a d i o"
            " - Hotmixradio 80 - http://www.hotmixradio.fr"
            ),
        "http://streaming.hotmixradio.fm/hotmixradio-80-48.aac",
        (
            "#EXTINF:-1,H o t M i x R a d i o"
            " - Hotmixradio 80 - http://www.hotmixradio.fr"
            ),
        "http://streaming.hotmixradio.fm/hotmixradio-80-128.mp3",
        (
            "#EXTINF:-1,H o t M i x R a d i o"
            " - Hotmixradio 80 - http://www.hotmixradio.fr"
            ),
        "http://streaming.hotmixradio.fm/hotmixradio-80-128.mp3",
        ])
    expected_urls = [
        "http://streaming.hotmixradio.fm/hotmixradio-80-128.mp3",
        "http://streaming.hotmixradio.fm/hotmixradio-80-48.aac",
        "http://streaming.hotmixradio.fm/hotmixradio-80-128.mp3",
        "http://streaming.hotmixradio.fm/hotmixradio-80-128.mp3",
        ]

    # with a valid m3u
    assert url.parse_m3u(content) == expected_urls

    # with an empty string
    assert url.parse_m3u("") == []


def test_parse_pls():
    content = "\n".join([
        "[playlist]",
        "File1=http://str0.creacast.com/accent4",
        "Title1=Accent4 Alsace (live)",
        "Length1=0",
        "File2=http://str0.creacast.com/accent4",
        "Title2=Accent4 Alsace (live)",
        "Length2=0",
        "File3=http://str0.creacast.com/accent4",
        "Title3=Accent4 Alsace (live)",
        "Length3=0",
        "NumberOfEntries=3",
        "Version2",
        ])
    expected_urls = [
        "http://str0.creacast.com/accent4",
        "http://str0.creacast.com/accent4",
        "http://str0.creacast.com/accent4",
        ]

    # with a valid pls
    assert url.parse_pls(content) == expected_urls

    # with an empty string
    assert url.parse_pls("") == []


def test_extract_playlist():
    text = content
    expected_url = extracted_url
    assert url.extract_playlist(text, "m3u") == expected_url

    text = ""
    with pytest.raises(RuntimeError):
        url.extract_playlist(text, "m3u")


def test_acquire_playlist(requests):
    test_url = urls[0]
    expected_content = ""

    # failing
    answer = requests.get.return_value
    answer.ok = False
    assert url.acquire_playlist(test_url) == expected_content

    answer.reset_mock()
    # succeeding
    expected_content = content
    answer.ok = True
    answer.text = expected_content
    assert url.acquire_playlist(test_url) == expected_content


def test_prepare_stream_urls(urltype, acquire_playlist, extract_playlist):
    expected_streams = prepared_urls

    urltype.side_effect = url_types
    acquire_playlist.side_effect = (content,)
    extract_playlist.side_effect = (extracted_url,)

    prepared_streams = url.prepare_stream_urls(urls)
    assert prepared_streams == expected_streams
