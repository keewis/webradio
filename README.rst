webradio
========

provides a framework and a binary for operating a raspberry pi based
internet radio.


framework
---------

usage (for creating a not-prebuffered player in '/tmp/webradio'):

.. code-block:: python
    import webradio

    with open("stations") as fd:
        urls = tuple(_.strip() for _ in fd)

    choice = 2  # given by user
    with webradio.single.map(basepath="/tmp/webradio", urls=urls) as client:
        client.play(choice)
