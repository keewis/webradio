import pathlib

import webradio.single as single


def test_fill(tmpdir):
    path = pathlib.Path(str(tmpdir))

    single.fill(path)

    mpd = path / "mpd"
    assert mpd.is_dir()
    expected_content = [
        mpd / name
        for name in ["database", "mpd.conf", "playlists"]
        ]
    assert sorted(mpd.iterdir()) == expected_content
    config = mpd / "mpd.conf"
    assert (mpd / "playlists").is_dir()
    assert config.is_file() and (mpd / "database").is_file()
    assert config.stat().st_size > 0
