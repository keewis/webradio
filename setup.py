from setuptools import setup

import webradio

setup(
    name='webradio',
    description=webradio.__doc__.split("\n", 1)[0],
    long_description=open("README.rst").read(),
    version=webradio.__version__,
    author="Justus",
    author_email="justus.magin@posteo.de",
    license='BSD',
    classifiers=[
        'Development Status :: 1 - Planning',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        ],
    packages=[
        "webradio",
        ],
    install_requires=[
        'requests',
        ],
    )
