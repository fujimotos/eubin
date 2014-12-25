#!/usr/bin/env python

import poplib
import ssl
import os
import socket
import time
import signal

class POP3Agent:
    def __init__(self, host, port, debug=0):
        self.pop3 = poplib.POP3(host, port)
        self.pop3.set_debuglevel(debug)

    def login(self, user, password, apop=False):
        if apop:
            self.pop3.apop(user, password)
        else:
            self.pop3.user(user)
            self.pop3.pass_(password)

    def fetchmail(self, destdir, leavecopy=True):
        maildir = Maildir(destdir)

        num, size = self.pop3.stat()
        for idx in range(num):
            msg, lines, octet = self.pop3.retr(idx+1)
            maildir.deliver(lines)

            if not leavecopy:
                self.pop3.dele(idx+1)

    def quit(self):
        self.pop3.quit()

class POP3AgentSSL(POP3Agent):
    pass

class Maildir:
    def __init__(self, basedir):
        self.basedir = basedir
        self.pid = os.getpid()
        self.hostname = socket.gethostname()

    def get_uniqueid(self):
        now = int(time.time() * 1000)  # unix epoch in milliseconds
        return '{}.{}.{}'.format(now, self.pid, self.hostname)

    def deliver(self, lines):
        os.chdir(self.basedir)

        for retry in range(10):
            uid = self.get_uniqueid()
            tmpfile, newfile = os.path.join('tmp', uid), os.path.join('new',  uid)
            try:
                os.stat(tmpfile)
            except FileNotFoundError:
                break
            except:
                time.sleep(2)
        else:
            raise OSError('cannot safely create a file on tmp/')

        signal.alarm(86400) # 24-hour timer.

        with open(tmpfile, 'wb') as fw:
            for line in lines:
                fw.write(line + b'\n')

        os.link(tmpfile, newfile)
        os.remove(tmpfile)
