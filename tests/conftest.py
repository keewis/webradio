import pathlib
import sys


def get_root():
    tests_dir = pathlib.Path(__file__).parent
    root = tests_dir.absolute().parent
    return str(root)


sys.path.insert(0, get_root())

# so that the fixtures get recognised
from testutils.fixtures import *
