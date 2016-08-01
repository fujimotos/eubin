#!/usr/bin/env python3

import os


def load(path):
    if not os.path.exists(path):
        return set()
    with open(path, 'rb') as fp:
        return set(line.strip() for line in fp)


def save(path, state):
    tmpfile = path + '.tmp'
    with open(tmpfile, 'wb') as fp:
        for uid in state:
            fp.write(uid + b'\n')
    os.rename(tmpfile, path)
