#!/usr/bin/env python3

import socket
import os
import time

class MockServer:
    """A base class for server stub"""
    def __init__(self, host='localhost', port=0):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((host, port))
        self.server_socket.listen(1)
        self.client_socket = None

        # The MockServer class is intended to be used in a 'log-based' testing
        # for client scripts. It buffers all the input passed by the client, 
        # so, after executing some test pattern, you can inspect the log and
        # check if the desired conditions were fulfilled.
        self._recvlog = []

    def accept(self):
        socket, address = self.server_socket.accept()
        self.client_socket = socket

    def exit(self):
        if self.client_socket:
            self.client_socket.close()
        self.server_socket.close()

    def get_conninfo(self):
        return self.server_socket.getsockname()

    def get_logiter(self):
        return (line for line in self._recvlog)

    # Low level API
    def sendline(self, data=b'', eol=b'\r\n'):
        line = data + eol
        self.client_socket.send(line)

    def recvline(self, eol=b'\r\n'):
        line = b''
        while True:
            bt = self.client_socket.recv(1)
            if not bt:
                break
            line += bt
            if line[-2:] == eol:
                break
        self._recvlog.append(line)
        return line

class POP3Server(MockServer):
    """A POP3 server stub"""
    def __init__(self):
        super(POP3Server, self).__init__()

        # fake data
        self.msg_id = b''
        self.maildrop = []
        self.mailcount = 0
        self.dropsize = 0

    def set_fakedata(self, msg_id, maildrop, mailcount, dropsize):
        self.msg_id = msg_id
        self.maildrop = maildrop
        self.mailcount = mailcount
        self.dropsize = dropsize

    def greeting(self):
        self.sendline(b'+OK Greetings, human! ' + self.msg_id)

    # Stub methods
    def do_stat(self):
        resp = '+OK {} {}'.format(self.mailcount, self.dropsize).encode()
        self.sendline(resp)

    def do_retr(self, idx):
        self.sendline(b'+OK')
        for line in self.maildrop[idx]:
            self.sendline(line)
        self.sendline(b'.')

    def do_dele(self, idx):
        self.sendline(b'+OK message deleted')

    def do_apop(self, user, md5):
        self.sendline(b'+OK apop login successful')

    def do_user(self, user):
        self.sendline(b'+OK valid user name')

    def do_pass(self, password):
        self.sendline(b'+OK login successful')

    def do_quit(self):
        self.sendline(b'+OK')
        raise EOFError

    def talkback(self, line):
        if not line:
            raise EOFError
        tokens = line.decode().rstrip().split(' ')
        cmd, args = tokens[0].lower(), tokens[1:]
        getattr(self, 'do_' + cmd)(*args)

    # Running server
    def run(self):
        self.accept()
        self.greeting()
        while True:
            line = self.recvline()
            try:
                self.talkback(line)
            except EOFError:
                break
        self.exit()
