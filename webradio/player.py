from . import pool
from . import single


class Player(object):
    def __init__(self, *, basepath, urls, prebuffering=False):
        pass

    @property
    def prebuffering(self):
        pass

    @prebuffering.setter
    def prebuffering(self, new_state):
        pass

    def __getattr__(self, name):
        # forward to the current player
        pass
