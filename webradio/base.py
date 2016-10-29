import abc
from contextlib import contextmanager


@contextmanager
def ignore(exception):
    try:
        yield
    except exception:
        pass


class base_client(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def __init__(self, server, *, muted=False):
        """ constructor of the music client

        Parameters
        ----------
        server : str or object with socket attribute
            the server to connect to

        Other Parameters
        ----------------
        muted : bool, default False
            the initial muted state of the server
        """

    @abc.abstractmethod
    def disconnect(self):
        """ destructor of the music client

        Disconnect from the server and clean up.
        """

    @abc.abstractmethod
    def __enter__(self):
        """ context manager entry function """

    @abc.abstractmethod
    def __exit__(self, *args):
        """ context manager exit function """

    @abc.abstractproperty
    def volume(self):
        """ the volume of the server

        Returns
        -------
        volume : int
            the current volume in percent. If the server was muted,
            this is the volume it had before being muted.
        """

    @volume.setter
    @abc.abstractmethod
    def volume(self, new_volume):
        """ change the volume of the server

        Assigning to it will change the volume of the server. The value is
        assumed to be the volume in percent and will always be casted to
        integer. Just as when reading the volume, writing it will only change
        the volume if not muted, otherwise it will be cached until unmuted.
        """

    @abc.abstractproperty
    def urls(self):
        """ urls of the radio stations

        Returns
        -------
        urls : list of str
            the list of the assigned radio stations
        """

    @urls.setter
    @abc.abstractmethod
    def urls(self, urls):
        """ change the radio stations

        Assigning will replace the current list of radio stations with the
        given ones.

        Parameters
        ----------
        urls : list of str
            a list of valid radio urls
        """

    @abc.abstractmethod
    def play(self, index):
        """ select the radio station to play

        Parameters
        ----------
        index : int
            the index of the radio station

        Raises
        ------
        RuntimeError
            if index is greater or equal to the number of available urls
        """

    @abc.abstractproperty
    def station(self):
        """ the currently active station

        Returns
        -------
        station : int
            the current station index

        Raises
        ------
        IndexError
            if no station is active
        """

    @station.setter
    @abc.abstractmethod
    def station(self, index):
        """ select the radio station to play

        this is a direct wrapper of `play()`

        Raises
        ------
        RuntimeError
            if index is greater or equal to the number of available urls
        """

    @abc.abstractproperty
    def muted(self):
        """ the current mute state

        Returns
        -------
        muted : bool
            whether or not the server is currently muted
        """

    @muted.setter
    @abc.abstractmethod
    def muted(self, value):
        """ change the current mute state

        Parameters
        ----------
        muted : bool
            Whether or not the server should be muted. If it already is muted
            and is requested to get muted, it does nothing.
        """

    @abc.abstractmethod
    def mute(self):
        """ mute the server

        This is just a convenience function that sets `muted` to `True`
        """

    @abc.abstractmethod
    def unmute(self):
        """ unmute the server

        This is just a convenience function that sets `muted` to `False`
        """

    @abc.abstractmethod
    def toggle_mute(self):
        """ toggle the current mute state

        This is just a convenience function that inverts the muted state
        """
