#!/usr/bin/env python3

import getopt
import sys
import os
import logging
from .pop3 import Client, ClientSSL
from .pidlock import PIDLock

_log = logging.getLogger(__name__)

def get_config():
    import configparser
    import glob

    os.chdir(os.path.expanduser('~/.eubin'))

    for filename in glob.iglob('*.conf'):
        config = configparser.ConfigParser()
        config.read(filename)
        yield (filename, config)

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
    debug_level = logging.WARNING

    opts, args = getopt.getopt(sys.argv[1:], 'v')
    for key, val in opts:
        if key == '-v':
            debug_level -= 10

    logging.basicConfig(level=debug_level)

    # Main
    for filename, config in get_config():
        server, account, retrieval, security = \
            (config[key] for key in ('server', 'account', 'retrieval', 'security'))

        # Initiate the connection
        host, port = server['host'], server['port']
        overssl = security.getboolean('overssl')

        if overssl:
            client = ClientSSL(host, port)
        else:
            client = Client(host, port)

        # Authorization
        user = account['user']
        password = get_password(account['pass'], account['passtype'])
        apop = security.getboolean('apop')

        client.login(user, password, apop=apop)

        # Do some transaction
        dest = os.path.expanduser(retrieval['dest'])
        leavecopy = retrieval.getboolean('leavecopy')

        stat = client.fetchmail(dest, leavecopy=leavecopy)

        _log.info('[%s] %s mails retrieved (%s bytes)', filename, *stat)

        # Enter the update state.
        client.quit()

if __name__ == '__main__':
    os.chdir(os.path.expanduser('~/.eubin'))
    with PIDLock('lockfile').acquire():
        main()
