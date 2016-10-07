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


def extract_playlist(text):
    urls = text.split("\n")
    filtered_urls = tuple(
        url.strip()
        for url in urls
        if not url.startswith('#') and urlparse(url).netloc != ""
        )

    if len(filtered_urls) == 0:
        raise RuntimeError("could not extract stream url")

    return filtered_urls[0]


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
