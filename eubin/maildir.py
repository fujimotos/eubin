#!/usr/bin/env python

import os
import time
import glob
import logging
from socket import gethostname
from binascii import hexlify

_log = logging.getLogger(__name__)

def _getuid():
    now = str(time.time()).split('.')
    urandom = hexlify(os.urandom(5)).decode()
    return '{}.M{}R{}P{}.{}'.format(now[0], now[1], urandom, os.getpid(), gethostname())

def deliver(maildir, lines):
    os.chdir(maildir)

    for retry in range(10):
        uid = _getuid()
        try:
            os.stat('tmp/' + uid)
        except FileNotFoundError:
            break
        except:
            pass
        time.sleep(2)
    else:
        raise OSError('cannot safely create a file on tmp/')

    tmpfile, newfile = 'tmp/' + uid, 'new/' + uid

    _log.debug("* New file: '%s'", newfile)

    with open(tmpfile, 'wb') as fw:
        for line in lines:
            fw.write(line + b'\n')

    os.link(tmpfile, newfile)
    os.remove(tmpfile)
    return uid

def cleanup(maildir):
    os.chdir(maildir)

    for path in glob.iglob('tmp/*'):
        if not os.path.isfile(path):
            continue

        atime = os.path.getatime(path)
        if (time.time() - atime) > 129600:  # Not accessed in 36 hours
            _log.debug("* Clean up: '%s'", path)
            os.remove(path)
