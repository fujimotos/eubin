#!/usr/bin/env python

import poplib
import os
import socket
import time

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

    def quit(self):
        self.pop3.quit()

class Maildir:
    def __init__(self, basedir):
        self.basedir = basedir
        self.pid = os.getpid()
        self.hostname = socket.gethostname()

    def get_uniqueid(self):
        now = int(time.time() * 1000)  # unix epoch in milliseconds
        return '{}.{}.{}'.format(now, self.pid, self.hostname)
