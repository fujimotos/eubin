#!/usr/bin/env python

import poplib
import ssl
import logging
import time
from . import maildir
from . import statelog

_log = logging.getLogger(__name__)


class Client:
    def __init__(self, host, port=110):
        _log.info('Connect to %s:%s [SSL=False]', host, port)
        self.pop3 = poplib.POP3(host, port)

    def stls(self):
        _log.info('Start TLS connection')
        context = ssl.create_default_context()
        self.pop3.stls(context=context)

    def login(self, user, password, apop=False):
        _log.debug('Login as %s [APOP=%s]', user, apop)
        if apop:
            self.pop3.apop(user, password)
        else:
            self.pop3.user(user)
            self.pop3.pass_(password)

    def fetch(self, destdir):
        _log.debug('Download to "%s" [COPY=False]', destdir)
        count, size = self.pop3.stat()

        for idx in range(count):
            msg, lines, octet = self.pop3.retr(idx+1)
            filename = maildir.deliver(destdir, lines)
            self.pop3.dele(idx+1)

    def fetch_copy(self, destdir, logpath, leavemax=None):
        count, size = self.pop3.stat()
        _log.debug('Download to "%s" [COPY=True]', destdir)
        _log.debug('%s messages in maildrop (%s bytes)', count, size)

        prev_state = statelog.load(logpath)
        state, retrieved = set(), []
        for line in self.pop3.uidl()[1]:
            tokens = line.split(b' ', 1)
            msgnum, uid = int(tokens[0]), tokens[1]

            if uid not in prev_state:
                msg, lines, octet = self.pop3.retr(msgnum)
                maildir.deliver(destdir, lines)
                retrieved.append(octet)

            # Leave last N messages on the spool.
            if leavemax and msgnum <= (count - leavemax):
                self.pop3.dele(msgnum)
            else:
                state.add(uid)

        statelog.save(logpath, state)
        _log.info('%s messages retrieved (%s bytes)',
                  len(retrieved), sum(retrieved))

    def quit(self):
        self.pop3.quit()


class ClientSSL(Client):
    def __init__(self, host, port=995):
        _log.info('Connect to %s:%s [SSL=True]', host, port)
        context = ssl.create_default_context()
        self.pop3 = poplib.POP3_SSL(host, port, context=context)
