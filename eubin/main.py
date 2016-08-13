#!/usr/bin/env python3

"""Usage: eubin [-v] [-q] [-h] [--version] [config_file]

options:
  -v/--verbose  - display debugging messages to stderr.
  -q/--quiet    - suppress (most of) warning messages.
  -h/--help     - print this message.
  --version     - output version information
"""

import sys
import os
import logging
import signal
import glob
from getopt import getopt
from configparser import ConfigParser
from fcntl import flock, LOCK_NB, LOCK_EX

from .util import get_client

_log = logging.getLogger(__name__)

VERSION = '1.1.0'
BASEDIR = os.path.expanduser('~/.eubin')


def fetch_new_mail(config_path):
    """Go to POP3 server and download new messages."""
    # Acquire an exclusive lock
    config_file = open(config_path, 'r')
    try:
        flock(config_file, (LOCK_EX | LOCK_NB))
    except BlockingIOError:
        _log.error('already running for "%s"', config_path)
        return

    # Parse config
    config = ConfigParser(inline_comment_prefixes=('#',))
    config.readfp(config_file)

    # Expand sections
    account = config['account']
    retrieval = config['retrieval']
    security = config['security']

    # Setup timer
    signal.alarm(retrieval.getint('timeout', 0))

    # Initiate the connection
    client = get_client(config)
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
        basedir, filename = os.path.split(config_path)
        logpath = os.path.join(basedir, '.{}.state'.format(filename))
        client.fetch_copy(dest, logpath=logpath, leavemax=leavemax)
    else:
        client.fetch(dest)

    client.quit()
    signal.alarm(0)
    config_file.close()


if __name__ == '__main__':
    debug_level = logging.INFO

    opts, args = getopt(sys.argv[1:], 'vqh',
                        ('verbose', 'quiet', 'help', 'version'))
    for key, val in opts:
        if key in ('-v', '--verbose'):
            debug_level -= 10
        elif key in ('-q', '--quiet'):
            debug_level += 10
        elif key in ('-h', '--help'):
            print(__doc__, file=sys.stderr)
            sys.exit(0)
        elif key in ('--version',):
            print('eubin {}'.format(VERSION), file=sys.stderr)
            sys.exit(0)

    logging.basicConfig(level=debug_level, style='{',
                        format='eubin[{levelname}]: {message}')

    if args:
        targets = [os.path.abspath(args[0])]
    else:
        targets = glob.iglob(os.path.join(BASEDIR, '*.conf'))

    for config_path in targets:
        fetch_new_mail(config_path)
