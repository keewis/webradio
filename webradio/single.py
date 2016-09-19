import pathlib
import subprocess
import shutil


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


class Server(object):
    def __init__(self, *, basepath):
        self.basepath = pathlib.Path(basepath).absolute()

        if self.basepath.exists():
            raise FileExistsError(
                "{} does already exist... not overwriting".format(
                    self.basepath,
                    ))

        self.basepath.mkdir(mode=0o700)

        fill(self.basepath)
        subprocess.call(
            ["/usr/bin/mpd"],
            env={'XDG_CONFIG_HOME': str(self.basepath.absolute())},
            )

    @property
    def socket(self):
        return self.basepath / "mpd" / "socket"

    def __del__(self):
        subprocess.call(
            ['/usr/bin/mpd', '--kill'],
            env={'XDG_CONFIG_HOME': str(self.basepath.absolute())},
            )
        try:
            mpd = self.basepath / "mpd"
            # only remove the mpd subtree using something like rm -rf
            shutil.rmtree(str(mpd.absolute()))

            # try to remove the basepath (if it's empty)
            self.basepath.rmdir()
        except (FileNotFoundError, OSError):
            pass
