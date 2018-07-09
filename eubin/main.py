"""Usage: eubin [-qhvV]

Options:

  -h  - Print this help message and exit
  -q  - Quiet mode. Cause eubin to suppress messages.
  -v  - Verbose mode. Cause eubin to output debugging messages.
  -V  - Show the software version and exit
"""

import sys
import os
import logging
import signal
import glob
import shlex
import fcntl
import getopt
import subprocess
import configparser

from .pop3 import Client, ClientSSL

_log = logging.getLogger(__name__)

VERSION = '1.2.1'
BASEDIR = os.path.expanduser('~/.eubin')

def lock_exnb(fp):
    try:
        fcntl.flock(fp, (fcntl.LOCK_EX | fcntl.LOCK_NB))
    except BlockingIOError:
        return -1
    return 0

def pass_eval(cmd):
    res = subprocess.check_output(shlex.split(cmd), universal_newlines=1)
    return res.rstrip('\n')

def get_logpath(config_path):
    head, tail = os.path.split(config_path)
    name = '.{}.state'.format(tail)
    return os.path.join(head, name)

def load_config(config_path):
    config = configparser.ConfigParser(inline_comment_prefixes=('#',))
    with open(config_path, 'r') as fp:
        config.readfp(fp)

    if 'pass_eval' in config['account']:
        password = pass_eval(config['account']['pass_eval'])
    else:
        password = config['account']['pass']

    dest = os.path.expanduser(config['retrieval']['dest'])

    leavemax = None
    if config['retrieval'].get('leavemax'):
        leavemax = int(retrieval['leavemax'])

    return {
        'host': config['server']['host'],
        'port': config['server']['port'],
        'user': config['account']['user'],
        'password': password,
        'apop': config['security'].getboolean('apop'),
        'overssl': config['security'].getboolean('overssl'),
        'starttls': config['security'].getboolean('starttls'),
        'noverifycert': config['security'].getboolean('noverifycert'),
        'timeout': config['retrieval'].getint('timeout', 0),
        'leavecopy': config['retrieval'].getboolean('leavecopy'),
        'dest': dest,
        'leavemax': leavemax,
        'logpath': get_logpath(config_path),
    }

def fetch_new_mail(config_path):
    _log.debug('--------- %s ---------', os.path.basename(config_path))

    lockfile = open(config_path, 'r')
    if lock_exnb(lockfile):
        return _log.error('already running for "%s"', config_path)

    conf = load_config(config_path)

    signal.alarm(conf['timeout'])

    if conf['overssl']:
        client = ClientSSL(conf['host'], conf['port'], conf['noverifycert'])
    else:
        client = Client(conf['host'], conf['port'])

    if conf['starttls']:
        client.stls()

    client.login(user=conf['user'],
                 password=conf['password'],
                 apop=conf['apop'])

    if conf['leavecopy']:
        client.fetch_copy(conf['dest'], conf['logpath'], conf['leavemax'])
    else:
        client.fetch(conf['dest'])

    client.quit()
    signal.alarm(0)
    lockfile.close()

def main():
    debug_level = logging.INFO

    opts, args = getopt.getopt(sys.argv[1:], 'hqvV')
    for key, val in opts:
        if key == '-h':
            print(__doc__, file=sys.stderr)
            return 0
        elif key == '-q':
            debug_level += 10
        elif key == '-v':
            debug_level -= 10
        elif key == '-V':
            print('eubin {}'.format(VERSION), file=sys.stderr)
            return 0

    logging.basicConfig(level=debug_level, style='{',
                        format='eubin[{levelname}]: {message}')

    if args:
        targets = [os.path.abspath(args[0])]
    else:
        targets = glob.iglob(os.path.join(BASEDIR, '*.conf'))

    for config_path in targets:
        fetch_new_mail(config_path)

if __name__ == '__main__':
    sys.exit(main())
