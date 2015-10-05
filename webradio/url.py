from urllib.parse import urlparse
from posixpath import splitext


def urltype(url):
    path = urlparse(url).path
    root, ext = splitext(path)
    if ext == "":
        return "direct"
    else:
        return "playlist"
