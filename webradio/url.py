from urllib.parse import urlparse
from posixpath import splitext
import requests


def urltype(url):
    path = urlparse(url).path
    root, ext = splitext(path)
    if ext == "":
        return "direct"
    else:
        return "playlist"


def extract_playlist(text):
    urls = text.split("\n")
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
    ordered_urls = tuple(enumerate(urls))
    playlistdict = tuple(
        (index, acquire_playlist(url))
        for index, url in ordered_urls
        if urltype(url) == "playlist"
        )

    urls = tuple(
        url
        if index != mod_index
        else extract_playlist(mod_url)
        for index, url in ordered_urls
        for mod_index, mod_url in playlistdict
        )

    return urls
