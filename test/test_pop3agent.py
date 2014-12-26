import unittest
from threading import Thread
from mockserver import POP3Server
from pop3agent import POP3Agent, Maildir

class TestPOP3Agent(unittest.TestCase):
    def setUp(self):
        self.server = POP3Server()
        self.server.set_respdict({
            'greeting': b'+OK Greetings, Human! <message-id>\r\n',
            'user': b'+OK Valid user\r\n',
            'pass': b'+OK Passowrd ok\r\n',
            'apop': b'+OK Authentication successful\r\n',
            'stat': b'+OK 2 320\r\n',
            'retr': b'+OK\r\n<mail-text>\r\n.\r\n',
            'quit': b'+OK Good bye!'
        })
        self.host, self.port = self.server.get_conninfo()
        Thread(target=self.server.run).start()

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
        
        digest = b'88670a99aa1930515aae5569677fac19'  # md5sum(b'<message-id>passowrd')
        self.assertEqual(next(recvlog), b'APOP user ' + digest + b'\r\n')
        self.assertEqual(next(recvlog), b'QUIT\r\n')


class TestMaildir(unittest.TestCase):
    def test_get_uniqueid(self):
        m = Maildir('/tmp/')
        self.assertNotEqual(m.get_uniqueid(), m.get_uniqueid())

if __name__ == '__main__':
    unittest.main()
