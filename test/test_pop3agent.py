import unittest
import re
from threading import Thread
from mockserver import POP3Server
from pop3agent import POP3Agent

class TestPOP3Agent(unittest.TestCase):
    def setUp(self):
        self.server = POP3Server()
        self.host, self.port = self.server.get_conninfo()
        self.server.set_fakedata(
            msg_id = b'<message-id>',
            maildrop = ([b'msg1_line1', b'msg1_line2'], ['msg2_line1']),
            mailcount = 2,
            dropsize = 30
        )
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

if __name__ == '__main__':
    unittest.main()
