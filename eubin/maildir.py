#!/usr/bin/env python

import os
import socket
import time

def get_uniqueid():
    pid = os.getpid()
    hostname = socket.gethostname()
    epoch, microsec = str(time.time()).split('.')
    urandom = ''.join('{:02x}'.format(x) for x in os.urandom(5))
    return '{}.M{}R{}.{}'.format(epoch, microsec, urandom, self.hostname)

def deliver(lines, maildir):
    os.chdir(maildir)

    for retry in range(10):
        uid = self.get_uniqueid()
        tmpfile, newfile = os.path.join('tmp', uid), os.path.join('new',  uid)
        try:
            os.stat(tmpfile)
        except FileNotFoundError:
            break
        except:
            pass
        time.sleep(2)
    else:
        raise OSError('cannot safely create a file on tmp/')

    signal.alarm(86400) # 24-hour timer.

    with open(tmpfile, 'wb') as fw:
        for line in lines:
            fw.write(line + b'\n')

    os.link(tmpfile, newfile)
    os.remove(tmpfile)
    signal.alarm(0)


def clean(self, maildir):
    now = time.time()

    os.chdir(maildir)

    for filename in os.listdir('tmp/'):
        path = os.path.join('tmp/', filename)

        if not os.path.isfile(path):
            continue

        atime = os.path.getatime(path)
        if  (now - atime) > 129600:  # Not accessed in 36 hours
            os.remove(path)
