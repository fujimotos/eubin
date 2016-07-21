#!/usr/bin/env python

import poplib
import ssl
import logging
import time
from . import maildir
from . import hashlog

_log = logging.getLogger(__name__)

class Client:
    def __init__(self, host, port):
        self.pop3 = poplib.POP3(host, port)

    def stls(self):
        context = ssl.create_default_context()
        self.pop3.stls(context=context)

    def login(self, user, password, apop=False):
        if apop:
            self.pop3.apop(user, password)
        else:
            self.pop3.user(user)
            self.pop3.pass_(password)

    def fetch(self, destdir):
        count, size = self.pop3.stat()

        for idx in range(count):
            msg, lines, octet = self.pop3.retr(idx+1)
            filename = maildir.deliver(destdir, lines)
            self.pop3.dele(idx+1)

    def fetch_copy(self, destdir, logpath, leavemax=None):
        count, size = self.pop3.stat()
        maillog = hashlog.load(logpath)

        for idx in range(count):
            header = self.pop3.top(idx+1, 0)[1]
            md5sum = hashlog.md5sum(header)

            if md5sum not in maillog:
                msg, lines, octet = self.pop3.retr(idx+1)
                filename = maildir.deliver(destdir, lines)
                hashlog.append(logpath, md5sum)

            if leavemax and idx < (count - leavemax):
                self.pop3.dele(idx+1)

    def quit(self):
        self.pop3.quit()


class ClientSSL(Client):
    def __init__(self, host, port):
        context = ssl.create_default_context()
        self.pop3 = poplib.POP3_SSL(host, port, context=context)
