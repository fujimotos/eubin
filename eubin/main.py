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

from .util import get_client, get_password, lock_exnb, get_logpath

_log = logging.getLogger(__name__)

VERSION = '1.1.0'
BASEDIR = os.path.expanduser('~/.eubin')


def fetch_new_mail(config_path):
    """Go to POP3 server and download new messages."""
    # Acquire an exclusive lock
    config_file = open(config_path, 'r')

    if lock_exnb(config_file) != 0:
        return _log.error('already running for "%s"', config_path)

    # Parse config
    config = ConfigParser(inline_comment_prefixes=('#',))
    config.readfp(config_file)

    # Expand sections
    retrieval = config['retrieval']
    security = config['security']

    # Setup timer
    signal.alarm(retrieval.getint('timeout', 0))

    # Initiate the connection
    client = get_client(config)
    client.login(user=config['account']['user'],
                 password=get_password(config),
                 apop=security.getboolean('apop'))

    # Do some transaction
    dest = os.path.expanduser(retrieval['dest'])

    leavemax = None
    if retrieval.get('leavemax'):
        leavemax = int(retrieval['leavemax'])

    if retrieval.getboolean('leavecopy'):
        logpath = get_logpath(config_path)
        client.fetch_copy(dest, logpath, leavemax)
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
