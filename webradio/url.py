from urllib.parse import urlparse
from posixpath import splitext
import requests


def urltype(url):
    """ determine the type of the given url

    Parameters
    ----------
    url : string
        the url to parse


    Returns
    -------
    type : string
        the determined url type. This will currently be
            direct    for the stream url
            <type>    for the url of a playlist file, where <type>
                      is the type of the playlist file. Valid types
                      are: m3u and pls
    """
    playlist_extensions = [
        "m3u",
        "pls",
        ]

    path = urlparse(url).path
    root, ext = splitext(path)

    stripped_extension = ext.strip(".")
    if stripped_extension not in playlist_extensions:
        return "direct"
    else:
        return stripped_extension


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
        'direct': lambda url: [url]
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
    url_mapping = (
        (url, urltype(url))
        for url in urls
        )
    content_mapping = (
        (url if type == "direct" else acquire_playlist(url), type)
        for url, type in url_mapping
        )
    prepared_urls = tuple(
        extract_playlist(content, type)
        for content, type in content_mapping
        )

    return prepared_urls
