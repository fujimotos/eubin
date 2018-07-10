import unittest
import tempfile
import shutil
import os
from tempfile import TemporaryDirectory
from threading import Thread
from eubin import pop3
from mockserver import POP3Server

class TestStatelog(unittest.TestCase):
    def setUp(self):
        self.tmpdir = TemporaryDirectory()
        self.logpath = os.path.join(self.tmpdir.name, 'statelog')
        self.nonexist = os.path.join(self.tmpdir.name, 'nonexist')

        with open(self.logpath, 'wb') as fw:
            fw.write(b'001\n')
            fw.write(b'002\n')

    def tearDown(self):
        self.tmpdir.cleanup()

    def test_load(self):
        state = pop3.statelog_load(self.logpath)
        self.assertEqual(state, {b'001', b'002'})

    def test_load_fallback(self):
        state = pop3.statelog_load(self.nonexist)
        self.assertEqual(state, set())

    def test_create(self):
        pop3.statelog_save(self.logpath, {b'001', b'002'})
        with open(self.logpath, 'rb') as fp:
            self.assertEqual(fp.readline(), b'001\n')
            self.assertEqual(fp.readline(), b'002\n')


class TestPOP3(unittest.TestCase):
    def setUp(self):
        # Mocking POP3 server
        self.server = POP3Server()
        self.server.set_respdict({
            'greeting': b'+OK Greetings, Human! <message-id>\r\n',
            'user': b'+OK Valid user\r\n',
            'pass': b'+OK Passowrd ok\r\n',
            'apop': b'+OK Authentication successful\r\n',
            'stat': b'+OK 2 320\r\n',
            'dele': b'+OK Mark the mail as deleted.\r\n',
            'retr': b'+OK\r\n<mail-text>\r\n.\r\n',
            'quit': b'+OK Good bye!',
            'top': b'+OK\r\n<header>\r\n.\r\n',
            'uidl': b'+OK\r\n1 001\r\n2 002\r\n.\r\n',
        })
        self.host, self.port = self.server.get_conninfo()
        Thread(target=self.server.run).start()

        # Set up a mailbox
        self.mailbox = tempfile.mkdtemp()
        for dirname in ('new', 'cur', 'tmp'):
            os.mkdir(os.path.join(self.mailbox, dirname))

        # Set up a hashlog
        self.hashlog = tempfile.NamedTemporaryFile()

    def tearDown(self):
        shutil.rmtree(self.mailbox)
        self.hashlog.close()

    def test_login(self):
        client = pop3.Client(self.host, self.port)
        client.login('user', 'password')
        client.quit()

        recvlog = self.server.get_logiter()

        self.assertEqual(next(recvlog), b'USER user\r\n')
        self.assertEqual(next(recvlog), b'PASS password\r\n')
        self.assertEqual(next(recvlog), b'QUIT\r\n')

    def test_login_apop(self):
        client = pop3.Client(self.host, self.port)
        client.login('user', 'password', apop=True)
        client.quit()

        recvlog = self.server.get_logiter()
        
        self.assertEqual(next(recvlog), b'APOP user 88670a99aa1930515aae5569677fac19\r\n')
        self.assertEqual(next(recvlog), b'QUIT\r\n')

    def test_fetch(self):
        client = pop3.Client(self.host, self.port)
        client.login('user', 'password')
        client.fetch(self.mailbox)
        client.quit()

        recvlog = self.server.get_logiter()

        self.assertEqual(next(recvlog), b'USER user\r\n')
        self.assertEqual(next(recvlog), b'PASS password\r\n')
        self.assertEqual(next(recvlog), b'STAT\r\n')
        self.assertEqual(next(recvlog), b'RETR 1\r\n')
        self.assertEqual(next(recvlog), b'DELE 1\r\n')
        self.assertEqual(next(recvlog), b'RETR 2\r\n')
        self.assertEqual(next(recvlog), b'DELE 2\r\n')
        self.assertEqual(next(recvlog), b'QUIT\r\n')

    def test_fetch_copy(self):
        client = pop3.Client(self.host, self.port)
        client.login('user', 'password')
        client.fetch_copy(self.mailbox, logpath=self.hashlog.name)
        client.fetch_copy(self.mailbox, logpath=self.hashlog.name) # Retry
        client.quit()

        recvlog = self.server.get_logiter()

        self.assertEqual(next(recvlog), b'USER user\r\n')
        self.assertEqual(next(recvlog), b'PASS password\r\n')
        self.assertEqual(next(recvlog), b'STAT\r\n')
        self.assertEqual(next(recvlog), b'UIDL\r\n')
        self.assertEqual(next(recvlog), b'RETR 1\r\n')
        self.assertEqual(next(recvlog), b'RETR 2\r\n')
        self.assertEqual(next(recvlog), b'STAT\r\n')
        self.assertEqual(next(recvlog), b'UIDL\r\n')
        self.assertEqual(next(recvlog), b'QUIT\r\n')

    def test_fetch_contents(self):
        client = pop3.Client(self.host, self.port)
        client.login('user', 'password')
        client.fetch(self.mailbox)
        client.quit()

        # Enter into 'new' directory of the mailbox.
        os.chdir(os.path.join(self.mailbox, 'new'))

        # There must be two mails exactly.
        mails = os.listdir('./')
        self.assertEqual(len(mails), 2)

        # Check the contents of these mails.
        for mail in mails:
            with open(mail, 'rb') as fp:
                self.assertEqual(fp.read(), b'<mail-text>\n')

if __name__ == '__main__':
    unittest.main()
