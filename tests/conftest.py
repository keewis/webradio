import os.path
import sys

# so that the fixtures get recognised
from testutils.fixtures import stdin, fake_client


def get_root():
    tests_dir, _ = os.path.split(__file__)
    return os.path.abspath(os.path.join(tests_dir, ".."))


sys.path.insert(0, get_root())
