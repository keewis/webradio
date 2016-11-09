from urllib.parse import urlparse
from posixpath import splitext
import requests


def urltype(url):
    """ determine the type of the given url

    this will currently be
    direct    for the stream url
    playlist  for the url of a playlist file
              extensions are normally m3u, pls or asx
    """
    path = urlparse(url).path
    root, ext = splitext(path)
    if ext == "":
        return "direct"
    else:
        return "playlist"


def playlist_type(url):
    path = urlparse(url).path
    root, ext = splitext(path)

    return ext.strip(".")


def parse_m3u(text):
    urls = [
        line.strip()
        for line in text.split("\n")
        if not line.startswith('#') and urlparse(line).netloc != ""
        ]

    return urls


def parse_pls(text):
    urls = [
        line.strip().split("=")[-1]
        for line in text.split("\n")
        if line.startswith("File")
        ]

    return urls


def extract_playlist(text, type):
    def unknown_type(text):
        raise RuntimeError("unknown type: {}".format(type))

    parsers = {
        'm3u': parse_m3u,
        'pls': parse_pls,
        }

    parser = parsers.get(type, unknown_type)
    urls = parser(text)

    if len(urls) == 0:
        raise RuntimeError("could not extract stream url")

    return urls[0]


def acquire_playlist(url):
    answer = requests.get(url)
    if not answer.ok:
        return ""
    else:
        return answer.text


def prepare_stream_urls(urls):
    prepared_urls = tuple(
        extract_playlist(acquire_playlist(url))
        if urltype(url) == "playlist"
        else url
        for url in urls
        )

    return prepared_urls
