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

    def fetchmail_copy(self, destdir, logpath, leavemax=None):
        count, size = self.pop3.stat()
        maillog = hashlog.load(logpath)
        self._state['maillog'] = logpath

        for idx in range(count):
            header = self.pop3.top(idx+1, 0)[1]
            md5sum = hashlog.md5sum(header)

            if md5sum not in maillog:
                msg, lines, octet = self.pop3.retr(idx+1)
                filename = maildir.deliver(destdir, lines)

                self._trace_mail(octet, filename, md5sum)
                hashlog.append(logpath, md5sum)

            if leavemax and leavemax <= idx:
                self.pop3.dele(idx+1)

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
            'cipher': self.pop3.sock.cipher(),
            'option': self._decode_ssl_options(context.options)
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

    @staticmethod
    def _decode_ssl_options(options):
        # This is the full list of ssl options defined in include/ssl.h
        # at openssl-1.0.1k.
        openssl_options = {
            0x00000001: 'SSL_OP_MICROSOFT_SESS_ID_BUG',
            0x00000002: 'SSL_OP_NETSCAPE_CHALLENGE_BUG',
            0x00000004: 'SSL_OP_LEGACY_SERVER_CONNECT',
            0x00000008: 'SSL_OP_NETSCAPE_REUSE_CIPHER_CHANGE_BUG',
            0x00000010: 'SSL_OP_TLSEXT_PADDING',
            0x00000020: 'SSL_OP_MICROSOFT_BIG_SSLV3_BUFFER',
            0x00000040: 'SSL_OP_SAFARI_ECDHE_ECDSA_BUG',
            0x00000080: 'SSL_OP_SSLEAY_080_CLIENT_DH_BUG',
            0x00000100: 'SSL_OP_TLS_D5_BUG',
            0x00000200: 'SSL_OP_TLS_BLOCK_PADDING_BUG',
            0x00000800: 'SSL_OP_DONT_INSERT_EMPTY_FRAGMENTS',
            0x80000BFF: 'SSL_OP_ALL',
            0x00001000: 'SSL_OP_NO_QUERY_MTU',
            0x00002000: 'SSL_OP_COOKIE_EXCHANGE',
            0x00004000: 'SSL_OP_NO_TICKET',
            0x00008000: 'SSL_OP_CISCO_ANYCONNECT',
            0x00010000: 'SSL_OP_NO_SESSION_RESUMPTION_ON_RENEGOTIATION',
            0x00020000: 'SSL_OP_NO_COMPRESSION',
            0x00040000: 'SSL_OP_ALLOW_UNSAFE_LEGACY_RENEGOTIATION',
            0x00080000: 'SSL_OP_SINGLE_ECDH_USE',
            0x00100000: 'SSL_OP_SINGLE_DH_USE',
            0x00400000: 'SSL_OP_CIPHER_SERVER_PREFERENCE',
            0x00800000: 'SSL_OP_TLS_ROLLBACK_BUG',
            0x01000000: 'SSL_OP_NO_SSLv2',
            0x02000000: 'SSL_OP_NO_SSLv3',
            0x04000000: 'SSL_OP_NO_TLSv1',
            0x08000000: 'SSL_OP_NO_TLSv1_2',
            0x10000000: 'SSL_OP_NO_TLSv1_1',
            0x20000000: 'SSL_OP_NETSCAPE_CA_DN_BUG',
            0x40000000: 'SSL_OP_NETSCAPE_DEMO_CIPHER_CHANGE_BUG',
            0x80000000: 'SSL_OP_CRYPTOPRO_TLSEXT_BUG'
        }

        res = []
        for key in sorted(openssl_options.keys()):
            if key & options:
                res.append(openssl_options[key])
        return res

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
