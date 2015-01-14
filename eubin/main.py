#!/usr/bin/env python3

import getopt
import sys
import os
import logging
from . import pop3
from .pidlock import PIDLock

_log = logging.getLogger(__name__)

# init
BASEDIR = os.path.expanduser('~/.eubin')
LOCKFILE = os.path.join(BASEDIR, 'lockfile')

# utils
def get_config():
    import configparser
    import glob

    pat = os.path.join(BASEDIR, '*.conf')
    for filename in glob.iglob(pat):
        config = configparser.ConfigParser()
        config.read(filename)
        config._id = os.path.basename(filename).rstrip('.conf')
        yield config

def get_password(token, passtype):
    password = None

    if passtype == 'plain':
        password = token
    elif passtype == 'shell':
        import shlex
        from subprocess import check_output
        cmd = shlex.split(token)
        password = check_output(cmd).decode().strip()
    else:
        raise ValueError('unknown password type: {}'.format(passtype))

    return password

def main():
    debug_level = logging.INFO

    opts, args = getopt.getopt(sys.argv[1:], 'v', ('quiet', ))
    for key, val in opts:
        if key == '-v':
            debug_level -= 10
        elif key == '--quiet':
            debug_level += 10

    logging.basicConfig(level=debug_level, format='eubin[{levelname}]: {message}', style='{')

    # Main
    for config in get_config():
        server, account, retrieval, security = \
            (config[key] for key in ('server', 'account', 'retrieval', 'security'))

        # Initiate the connection
        host, port = server['host'], server['port']
        overssl = security.getboolean('overssl')

        _log.info("Connect to %s:%s [SSL=%s]", host, port, overssl)

        client = pop3.connect(host, port, ssl=overssl)

        # Authorization
        user = account['user']
        password = get_password(account['pass'], account['passtype'])
        apop = security.getboolean('apop')

        _log.debug('Login as %s [APOP=%s]', user, apop)

        client.login(user, password, apop=apop)

        # Do some transaction
        dest = os.path.expanduser(retrieval['dest'])
        leavecopy = retrieval.getboolean('leavecopy')
        leavemax = retrieval.getint('leavemax')

        _log.debug('Retrieve mails to %s [leavecopy=%s]', dest, leavecopy)

        if leavecopy:
            maillog = os.path.join(BASEDIR, '.{}.maillog'.format(config._id))
            client.fetchmail_copy(dest, logpath=maillog)
        else:
            client.fetchmail(dest)

        stat = tuple(m['size'] for m in client._state['mail'])
        _log.info('%s mails retrieved (%s bytes)', len(stat), sum(stat))

        # Enter the update state.
        client.quit()

if __name__ == '__main__':
    with PIDLock(LOCKFILE).acquire():
        main()
