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
        self._init_state()
        self.pop3 = poplib.POP3(host, port)

    def _init_state(self):
        self._state = {
            'init': time.time(),
            'mail': [],  # list of retlieved mails
            'quit': None
        }

    def _trace_mail(self, size, filename, md5sum=None):
        now = time.time()
        self._state['mail'].append({
            'time': now,
            'size': size,
            'filename': filename,
            'md5sum':  md5sum
        })

    def login(self, user, password, apop=False):
        if apop:
            self.pop3.apop(user, password)
        else:
            self.pop3.user(user)
            self.pop3.pass_(password)

    def fetchmail(self, destdir):
        count, size = self.pop3.stat()

        for idx in range(count):
            msg, lines, octet = self.pop3.retr(idx+1)
            filename = maildir.deliver(destdir, lines)
            self.pop3.dele(idx+1)
            self._trace_mail(octet, filename)

    def fetchmail_copy(self, destdir, logpath):
        count, size = self.pop3.stat()
        maillog = hashlog.load(logpath)

        newmail = []
        for idx in range(count):
            header = self.pop3.top(idx+1, 0)[1]
            md5sum = hashlog.md5sum(header)

            if md5sum not in maillog:
                msg, lines, octet = self.pop3.retr(idx+1)
                filename = maildir.deliver(destdir, lines)

                self._trace_mail(octet, filename, md5sum)
                hashlog.append(logpath, md5sum)

    def quit(self):
        from pprint import pformat
        self.pop3.quit()

        self._state['quit'] = time.time()
        logging.debug('execlog = %s', pformat(self._state))


class ClientSSL(Client):
    def __init__(self, host, port):
        self._init_state()

        context = self.get_ssl_context()
        self.pop3 = poplib.POP3_SSL(host, port, context=context)

        self._state['ssl'] = {
            'version': ssl.OPENSSL_VERSION,
            'cipher': self.pop3.sock.cipher()
        }

    @staticmethod
    def get_ssl_context():
        # These settings below are based on ssl.get_default_context()
        # method (intoroduced in Python 3.4) with some modifications.
        # cf. https://docs.python.org/3.4/library/ssl.html#ssl.create
        #     _default_context
        context = ssl.SSLContext(ssl.PROTOCOL_SSLv23)

        # SSLv2/SSLv3 is known to be insecure. 
        # TODO: Wait untill Python3.4 is widely adapted enough, then
        #       disable TLSv1.0 as well.
        context.options |= ssl.OP_NO_SSLv2
        context.options |= ssl.OP_NO_SSLv3

        # Disable TLS compression
        context.options |= ssl.OP_NO_COMPRESSION

        # Disable some insecure ciphres
        context.set_ciphers('HIGH:!NULL:!eNULL:!aNULL:!RC4:!DSS:!MD5')

        # Always requires certifications.
        context.verify_mode = ssl.CERT_REQUIRED

        # Load default certificates.
        context.set_default_verify_paths()

        return context

# An interface function for Client/ClientSSL.
# Use this function as follows:
# >>> from eubin import pop3
# >>> client = pop3.connect('example.com', 111)
def connect(host, port, ssl=False):
    if ssl:
        client = ClientSSL(host, port)
    else:
        client = Client(host, port)
    return client
