#!/usr/bin/env python

import argparse
from webradio import url

parser = argparse.ArgumentParser()
parser.add_argument("streams_file")
parser.add_argument("urls_file")
args = parser.parse_args()

with open(args.streams_file) as filelike:
    in_streams = [line.strip() for line in filelike]

prepared_urls = url.prepare_stream_urls(in_streams)

with open(args.urls_file, 'w') as filelike:
    filelike.write("\n".join(prepared_urls))
