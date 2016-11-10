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
def parse_m3u():
    m = mock.patch(
        'webradio.url.parse_m3u',
        mock.create_autospec(url.parse_m3u),
        )

    with m as parse_m3u:
        yield parse_m3u


@pytest.fixture(scope='function')
def parse_pls():
    m = mock.patch(
        'webradio.url.parse_pls',
        mock.create_autospec(url.parse_pls),
        )

    with m as parse_pls:
        yield parse_pls


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
    "http://www.hotmixradio.fr/hotmix80.m3u",
    "http://players.creacast.com/creacast/accent4/playlist.pls",
    "http://ice19.infomaniak.ch:80/jazzblues-high.mp3",
    "http://stream-sd.radioparadise.com:8056",
    "http://icecast2.rte.ie/ieradio1",
    )
prepared_urls = (
    "http://streaming.hotmixradio.fm/hotmixradio-80-128.mp3",
    "http://str0.creacast.com/accent4",
    "http://ice19.infomaniak.ch:80/jazzblues-high.mp3",
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


def test_acquire_playlist(requests):
    test_url = urls[0]
    expected_content = "abcdef"

    # failing
    answer = requests.get.return_value
    answer.ok = False

    assert url.acquire_playlist(test_url) == ""

    # succeeding
    answer.ok = True
    answer.text = expected_content
    assert url.acquire_playlist(test_url) == expected_content


def test_extract_playlist(parse_m3u, parse_pls):
    content = ""
    urls = list(map(lambda x: "x{}".format(x), range(5)))
    type = "m3u"

    # succeeding parse
    parse_m3u.return_value = urls
    assert url.extract_playlist(content, type) == urls[0]

    # failing parse
    parse_m3u.return_value = []
    with pytest.raises(RuntimeError):
        url.extract_playlist(content, type)

    # direct type
    content = "abcdef"
    assert url.extract_playlist(content, "direct") == content

    # unknown type
    parse_m3u.return_value = urls
    with pytest.raises(RuntimeError):
        url.extract_playlist(content, "unkown")


def test_prepare_stream_urls(urltype, acquire_playlist, extract_playlist):
    expected_streams = prepared_urls

    urltype.side_effect = url_types
    acquire_playlist.side_effect = (content,)
    extract_playlist.side_effect = (extracted_url,)

    prepared_streams = url.prepare_stream_urls(urls)
    assert prepared_streams == expected_streams
