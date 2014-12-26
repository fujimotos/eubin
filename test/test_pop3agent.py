import unittest
import tempfile
import shutil
import os
from threading import Thread
from mockserver import POP3Server
from pop3agent import POP3Agent, Maildir

class TestPOP3Agent(unittest.TestCase):
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
            'quit': b'+OK Good bye!'
        })
        self.host, self.port = self.server.get_conninfo()
        Thread(target=self.server.run).start()

        # Set up a mailbox
        self.mailbox = tempfile.mkdtemp()
        for dirname in ('new', 'cur', 'tmp'):
            os.mkdir(os.path.join(self.mailbox, dirname))

    def tearDown(self):
        shutil.rmtree(self.mailbox)

    def test_login(self):
        agent = POP3Agent(self.host, self.port)
        agent.login('user', 'password')
        agent.quit()

        recvlog = self.server.get_logiter()

        self.assertEqual(next(recvlog), b'USER user\r\n')
        self.assertEqual(next(recvlog), b'PASS password\r\n')
        self.assertEqual(next(recvlog), b'QUIT\r\n')

    def test_login_apop(self):
        agent = POP3Agent(self.host, self.port)
        agent.login('user', 'password', apop=True)
        agent.quit()

        recvlog = self.server.get_logiter()
        
        self.assertEqual(next(recvlog), b'APOP user 88670a99aa1930515aae5569677fac19\r\n')
        self.assertEqual(next(recvlog), b'QUIT\r\n')

    def test_fetchmail(self):
        agent = POP3Agent(self.host, self.port)
        agent.login('user', 'password')
        agent.fetchmail(self.mailbox)
        agent.quit()

        recvlog = self.server.get_logiter()

        self.assertEqual(next(recvlog), b'USER user\r\n')
        self.assertEqual(next(recvlog), b'PASS password\r\n')
        self.assertEqual(next(recvlog), b'STAT\r\n')
        self.assertEqual(next(recvlog), b'RETR 1\r\n')
        self.assertEqual(next(recvlog), b'RETR 2\r\n')
        self.assertEqual(next(recvlog), b'QUIT\r\n')

    def test_fetchmail_nocopy(self):
        agent = POP3Agent(self.host, self.port)
        agent.login('user', 'password')
        agent.fetchmail(self.mailbox, leavecopy=False)
        agent.quit()

        recvlog = self.server.get_logiter()

        self.assertEqual(next(recvlog), b'USER user\r\n')
        self.assertEqual(next(recvlog), b'PASS password\r\n')
        self.assertEqual(next(recvlog), b'STAT\r\n')
        self.assertEqual(next(recvlog), b'RETR 1\r\n')
        self.assertEqual(next(recvlog), b'DELE 1\r\n')
        self.assertEqual(next(recvlog), b'RETR 2\r\n')
        self.assertEqual(next(recvlog), b'DELE 2\r\n')
        self.assertEqual(next(recvlog), b'QUIT\r\n')

    def test_fetchmail_contents(self):
        agent = POP3Agent(self.host, self.port)
        agent.login('user', 'password')
        agent.fetchmail(self.mailbox)
        agent.quit()

        # Enter into 'new' directory of the mailbox.
        os.chdir(os.path.join(self.mailbox, 'new'))

        # There must be two mails exactly.
        mails = os.listdir('./')
        self.assertEqual(len(mails), 2)

        # Check the contents of these mails.
        for mail in mails:
            with open(mail, 'rb') as fp:
                self.assertEqual(fp.read(), b'<mail-text>\n')


class TestMaildir(unittest.TestCase):
    def test_get_uniqueid(self):
        m = Maildir('/tmp/')
        self.assertNotEqual(m.get_uniqueid(), m.get_uniqueid())

if __name__ == '__main__':
    unittest.main()
