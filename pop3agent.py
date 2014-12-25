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
    def __init__(self, host, port, debug=2):
        context = self.get_ssl_context()
        self.pop3 = poplib.POP3_SSL(host, port, context=context)
        self.pop3.set_debuglevel(debug)

    @staticmethod
    def get_ssl_context():
        """Create SSL context with security settings."""

        # These settings below are based on ssl.get_default_context()
        # method (intoroduced in Python 3.4) with some modifications.
        # cf. https://docs.python.org/3.4/library/ssl.html#ssl.create
        #     _default_context
        context = ssl.SSLContext(ssl.PROTOCOL_TLSv1)

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

#
# Main
def get_configs(confdir, suffix):
    import configparser

    for fname in os.listdir(confdir):
        path = os.path.join(confdir, fname)

        if not os.path.isfile(path) or not fname.endswith(suffix):
            continue

        config = configparser.ConfigParser(interpolation=None)
        config.read(path)

        yield config

def get_password(token, passtype):
    from subprocess import check_output
    import shlex

    password = None

    if passtype == 'plain':
        password = token
    elif passtype == 'shell':
        result = check_output(shlex.split(token))
        password = result.decode().rstrip('\n')
    else:
        raise ValueError('invalid password type: {}'.format(passtype))

    return password
