#!/usr/bin/env python3

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
