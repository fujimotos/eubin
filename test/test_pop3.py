import unittest
import tempfile
import shutil
import os
from threading import Thread
from eubin import pop3
from mockserver import POP3Server

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

    def test_fetchmail(self):
        client = pop3.Client(self.host, self.port)
        client.login('user', 'password')
        client.fetchmail(self.mailbox)
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

    def test_fetchmail_copy(self):
        client = pop3.Client(self.host, self.port)
        client.login('user', 'password')
        client.fetchmail_copy(self.mailbox, logpath=self.hashlog.name)
        client.quit()

        recvlog = self.server.get_logiter()

        self.assertEqual(next(recvlog), b'USER user\r\n')
        self.assertEqual(next(recvlog), b'PASS password\r\n')
        self.assertEqual(next(recvlog), b'STAT\r\n')
        self.assertEqual(next(recvlog), b'TOP 1 0\r\n')
        self.assertEqual(next(recvlog), b'RETR 1\r\n')
        self.assertEqual(next(recvlog), b'TOP 2 0\r\n')
        self.assertEqual(next(recvlog), b'RETR 2\r\n')
        self.assertEqual(next(recvlog), b'QUIT\r\n')

    def test_fetchmail_copy_retlieved(self):
        with open(self.hashlog.name, 'w') as fp:
            # md5sum '<header>'
            fp.write('cea964ac6a233b51fe5a28f7f4a40895\n')

        client = pop3.Client(self.host, self.port)
        client.login('user', 'password')
        client.fetchmail_copy(self.mailbox, logpath=self.hashlog.name)
        client.quit()

        recvlog = self.server.get_logiter()

        self.assertEqual(next(recvlog), b'USER user\r\n')
        self.assertEqual(next(recvlog), b'PASS password\r\n')
        self.assertEqual(next(recvlog), b'STAT\r\n')
        self.assertEqual(next(recvlog), b'TOP 1 0\r\n')
        self.assertEqual(next(recvlog), b'TOP 2 0\r\n')
        self.assertEqual(next(recvlog), b'QUIT\r\n')

    def test_fetchmail_contents(self):
        client = pop3.Client(self.host, self.port)
        client.login('user', 'password')
        client.fetchmail(self.mailbox)
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
