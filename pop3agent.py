#!/usr/bin/env python

import poplib
import ssl
import os
import socket
import time
import signal
import logging
_log = logging.getLogger(__name__)

class POP3Agent:
    def __init__(self, host, port):
        self.pop3 = poplib.POP3(host, port)

    def login(self, user, password, apop=False):
        if apop:
            self.pop3.apop(user, password)
        else:
            self.pop3.user(user)
            self.pop3.pass_(password)

    def fetchmail(self, destdir, leavecopy=True):
        maildir = Maildir(destdir)

        count, size = self.pop3.stat()
        for idx in range(count):
            msg, lines, octet = self.pop3.retr(idx+1)
            maildir.deliver(lines)

            if not leavecopy:
                self.pop3.dele(idx+1)
        return (count, size)

    def quit(self):
        self.pop3.quit()

class POP3AgentSSL(POP3Agent):
    def __init__(self, host, port):
        context = self.get_ssl_context()
        self.pop3 = poplib.POP3_SSL(host, port, context=context)

        _log.debug('OpenSSL information:')
        _log.debug('* Version: %s', ssl.OPENSSL_VERSION)
        _log.debug('* Cipher: %s', self.pop3.sock.cipher())
        _log.debug('* Compression: %s', self.pop3.sock.compression())

    @staticmethod
    def get_ssl_context():
        """Create SSL context with security settings."""

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

class Maildir:
    def __init__(self, basedir):
        self.basedir = basedir
        self.pid = os.getpid()
        self.hostname = socket.gethostname()

    def get_uniqueid(self):
        epoch, microsec = str(time.time()).split('.')
        urandom = ''.join('{:02x}'.format(x) for x in os.urandom(5))

        return '{}.M{}R{}.{}'.format(epoch, microsec, urandom, self.hostname)

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
                pass
            time.sleep(2)
        else:
            raise OSError('cannot safely create a file on tmp/')

        signal.alarm(86400) # 24-hour timer.

        with open(tmpfile, 'wb') as fw:
            for line in lines:
                fw.write(line + b'\n')

        os.link(tmpfile, newfile)
        signal.alarm(0)

#
# Main
def get_configs(confdir, suffix):
    import configparser

    for fname in os.listdir(confdir):
        path = os.path.join(confdir, fname)

        if not os.path.isfile(path) or not fname.endswith(suffix):
            continue

        _log.debug("Load %s.", path)

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

def main():
    logging.basicConfig(format='%(asctime)s\t%(message)s', level=logging.DEBUG)

    confdir = os.path.expanduser('~/.pop3agent')
    suffix = '.conf'

    for config in get_configs(confdir, suffix):
        server, account, retrieval, security = \
            (config[key] for key in ('server', 'account', 'retrieval', 'security'))

        # Initiate the connection
        host, port = server['host'], server['port']
        overssl = security.getboolean('overssl')

        _log.info('Connect to %s:%s [SSL=%s].', host, port, overssl)

        if overssl:
            agent = POP3AgentSSL(host, port)
        else:
            agent = POP3Agent(host, port)

        # Authorization
        user = account['user']
        password = get_password(account['pass'], account['passtype'])
        apop = security.getboolean('apop')

        _log.info("Login as '%s' [APOP=%s]", user, apop)
        agent.login(user, password, apop=apop)

        # Do some transaction
        dest = os.path.expanduser(retrieval['dest'])
        leavecopy = retrieval.getboolean('leavecopy')

        _log.info('Start fetching mails to %s [leavecopy=%s]', dest, leavecopy)
        stat = agent.fetchmail(dest, leavecopy=leavecopy)

        # Enter the update state.
        _log.info("Delivered: %s mails (%s bytes)", *stat)
        agent.quit()

if __name__ == '__main__':
    main()
