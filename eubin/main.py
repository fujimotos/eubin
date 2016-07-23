#!/usr/bin/env python3

"""Usage: eubin [-v] [-q] [-h] [--version] [config_file]

options:
  -v/--verbose  - display debugging messages to stderr.
  -q/--quiet    - suppress (most of) warning messages.
  -h/--help     - print this message.
  --version     - output version information
"""

version = '1.0.3'

import sys
import os
import logging
import signal
import glob
from getopt import getopt
from configparser import ConfigParser

from . import pop3
from .pidlock import PIDLock

_log = logging.getLogger(__name__)

BASEDIR = os.path.expanduser('~/.eubin')


def fetch_new_mail(config_path):
    """Go to POP3 server and download new messages."""
    # Parse config
    config = ConfigParser(inline_comment_prefixes=('#',))
    config.read(config_path)

    # Expand sections
    server = config['server']
    account = config['account']
    retrieval = config['retrieval']
    security = config['security']

    # Setup timer
    signal.alarm(retrieval.getint('timeout', 0))

    # Initiate the connection
    host, port = server['host'], server['port']

    if security.getboolean('overssl'):
        client = pop3.ClientSSL(host, port)
    else:
        client = pop3.Client(host, port)

    if security.getboolean('starttls'):
        client.stls()

    # Authorization
    client.login(user=account['user'],
                 password=account['pass'],
                 apop=security.getboolean('apop'))

    # Do some transaction
    dest = os.path.expanduser(retrieval['dest'])
    leavemax = retrieval.get('leavemax', '')

    if leavemax.isdigit():
        leavemax = int(leavemax)
    else:
        leavemax = None

    if retrieval.getboolean('leavecopy'):
        basedir, name = os.path.split(config_path)
        name = '.{}.maillog'.format(name.rstrip('conf'))
        logpath = os.path.join(basedir, name)
        client.fetch_copy(dest, logpath=logpath, leavemax=leavemax)
    else:
        client.fetch(dest)

    client.quit()
    signal.alarm(0)


if __name__ == '__main__':
    debug_level = logging.INFO

    opts, args = getopt(sys.argv[1:], 'vqh', ('verbose', 'quiet', 'help', 'version'))
    for key, val in opts:
        if key in ('-v', '--verbose'):
            debug_level -= 10
        elif key in ('-q', '--quiet'):
            debug_level += 10
        elif key in ('-h', '--help'):
            print(__doc__, file=sys.stderr)
            sys.exit(0)
        elif key in ('--version',):
            print('eubin {}'.format(version), file=sys.stderr)
            sys.exit(0)

    logging.basicConfig(level=debug_level, format='eubin[{levelname}]: {message}', style='{')

    if args:
        targets = [os.path.abspath(args[0])]
    else:
        targets = glob.iglob(os.path.join(BASEDIR, '*.conf'))

    for config_path in targets:
        with PIDLock(config_path + '.lockfile').acquire():
            fetch_new_mail(config_path)
