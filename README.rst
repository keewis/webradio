webradio
========

provides a framework and a binary for operating a raspberry pi based
internet radio.


framework
---------

usage (for a running mpd service with a socket at /var/run/mpd):

.. code-block:: python

    with open("stations") as fd:
       stations = tuple(_.strip() for _ in fd)
    choice = 2  # given by user
    with webradio.open("/var/run/mpd") as client:
        url = stations[choice] if choice < len(stations) else stations[-1]
        client.play(url)

