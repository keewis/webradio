config_template = """
music_directory    "~/Music"
playlist_directory "{base}/mpd/playlists"
db_file            "{base}/mpd/database"
log_file           "{base}/mpd/log"
pid_file           "{base}/mpd/pid"
state_file         "{base}/mpd/state"
sticker_file       "{base}/mpd/sticker.sql"

bind_to_address    "{base}/mpd/socket"

input {{
    plugin "curl"
}}

audio_output {{
    type        "alsa"
    name        "internal speakers"
    mixer_type  "software"
}}

replaygain    "off"
"""


def fill(path):
    mpdpath = path / "mpd"
    mpdpath.mkdir(mode=0o700)
    (mpdpath / "playlists").mkdir(mode=0o700)
    (mpdpath / "database").touch()
    with (mpdpath / "mpd.conf").open('w') as f:
        f.write(config_template.format(base=str(path.absolute())))
