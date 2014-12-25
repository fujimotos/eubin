import unittest
import re
from threading import Thread
from mockserver import POP3Server
from pop3agent import POP3Agent

class TestPOP3Agent(unittest.TestCase):
    def setUp(self):
        self.server = POP3Server()
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
        
        pat = re.compile(b'^APOP user [0-9a-z]{32}\r\n')
        self.assertTrue(pat.match(next(recvlog)))
        self.assertEqual(next(recvlog), b'QUIT\r\n')

if __name__ == '__main__':
    unittest.main()
