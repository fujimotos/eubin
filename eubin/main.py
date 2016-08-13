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

from .util import get_client, lock_exnb, get_logpath, sprint

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


def check_capability(config_path):
    config = ConfigParser(inline_comment_prefixes=('#',))
    config.read(config_path)

    client = get_client(config)
    sprint('Support APOP login?', client.check_apop())

    try:
        capa = client.get_capability()
    except Exception:
        return _log.error('CAPA command is not supported')

    sprint('Support UIDL (unique-id listing)?',  ('UIDL' in capa))
    sprint('Support STLS (Start-TLS)?', ('STLS' in capa))

    if 'SASL' in capa:
        sasl = ', '.join(capa['SASL'])
        sprint('Available SASL auth methods are', sasl)

    if 'EXPIRE' in capa:
        if capa['EXPIRE'][0] == '0':
            sprint('Leaving messages permitted by policy?', False)
        else:
            sprint('Leaving messages permitted by policy?', True)
            sprint('Retention days for messages', capa['EXPIRE'])

    if 'LOGIN-DELAY' in capa:
        sprint('Minimum seconds between logins',
               '{} sec'.format(capa['LOGIN-DELAY']))


if __name__ == '__main__':
    debug_level = logging.INFO
    handler = fetch_new_mail

    opts, args = getopt(sys.argv[1:], 'cvqh',
                        ('check', 'verbose', 'quiet', 'help', 'version'))
    for key, val in opts:
        if key in ('-v', '--verbose'):
            debug_level -= 10
        elif key in ('-q', '--quiet'):
            debug_level += 10
        elif key in ('-c', '--check'):
            handler = check_capability
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
        handler(config_path)
