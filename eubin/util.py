#!/usr/bin/env python3

import os
import fcntl

from . import pop3


def get_client(config):
    """Set up an instance of `pop3.Client(SSL)`"""
    host = config['server']['host']
    port = config['server']['port']
    security = config['security']

    if security.getboolean('overssl'):
        client = pop3.ClientSSL(host, port)
    else:
        client = pop3.Client(host, port)

    if security.getboolean('starttls'):
        client.stls()
    return client


def lock_exnb(fp):
    """Acquire an exclusive lock on `fp` using flock.
       Return 0 on success, -1 on error.
    """
    try:
        fcntl.flock(fp, (fcntl.LOCK_EX | fcntl.LOCK_NB))
    except BlockingIOError:
        return -1
    return 0


def get_logpath(config_path):
    head, tail = os.path.split(config_path)
    name = '.{}.state'.format(tail)
    return os.path.join(head, name)
