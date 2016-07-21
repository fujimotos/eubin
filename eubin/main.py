#!/usr/bin/env python3

"""Usage: eubin [-v] [-q] [-h] [--version]

options:
  -v/--verbose  - display debugging messages to stderr.
  -q/--quiet    - suppress (most of) warning messages.
  -h/--help     - print this message.
  --version     - output version information
"""

version = '1.0.3'

import getopt
import sys
import os
import logging
import signal
from . import pop3
from .pidlock import PIDLock

_log = logging.getLogger(__name__)

BASEDIR = os.path.expanduser('~/.eubin')
LOCKFILE = os.path.join(BASEDIR, 'lockfile')

def get_config():
    import configparser
    import glob

    pat = os.path.join(BASEDIR, '*.conf')
    for filename in glob.iglob(pat):
        config = configparser.ConfigParser(inline_comment_prefixes=('#',))
        config.read(filename)
        config._id = os.path.basename(filename).rstrip('.conf')
        yield config

def main():
    debug_level = logging.INFO

    opts, args = getopt.getopt(sys.argv[1:], 'vqh', ('verbose', 'quiet', 'help', 'version'))
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

    for config in get_config():
        server, account, retrieval, security = \
            (config[key] for key in ('server', 'account', 'retrieval', 'security'))

        # Setup timer
        timeout = retrieval.getint('timeout', 0)
        signal.alarm(timeout)

        # Initiate the connection
        host, port = server['host'], server['port']
        overssl = security.getboolean('overssl')

        _log.info("Connect to %s:%s [SSL=%s]", host, port, overssl)

        if overssl:
            client = pop3.ClientSSL(host, port)
        else:
            client = pop3.Client(host, port)

        if security.getboolean('starttls'):
            _log.info("Start TLS connection.")
            client.stls()

        # Authorization
        user = account['user']
        password = account['pass']
        apop = security.getboolean('apop')

        _log.debug('Login as %s [APOP=%s]', user, apop)

        client.login(user, password, apop=apop)

        # Do some transaction
        dest = os.path.expanduser(retrieval['dest'])
        leavecopy = retrieval.getboolean('leavecopy')
        leavemax = retrieval.get('leavemax')

        if leavemax.isdigit():
            leavemax = int(leavemax)
        else:
            leavemax = None

        _log.debug('Retrieve mails to %s [leavecopy=%s]', dest, leavecopy)

        if leavecopy:
            maillog = os.path.join(BASEDIR, '.{}.maillog'.format(config._id))
            client.fetch_copy(dest, logpath=maillog, leavemax=leavemax)
        else:
            client.fetch(dest)

        client.quit()
        signal.alarm(0)

if __name__ == '__main__':
    with PIDLock(LOCKFILE).acquire():
        main()
