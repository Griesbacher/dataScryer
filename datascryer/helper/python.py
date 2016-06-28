import sys
import time


def python_3():
    return sys.version_info[0] == 3


def xrange(start, stop, step):
    while start < stop:
        yield start
        start += step


def delta_ms(start):
    return (time.time() - start) * 1000
