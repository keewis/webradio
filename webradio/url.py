from urllib.parse import urlparse
from posixpath import splitext


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
