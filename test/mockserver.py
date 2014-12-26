#!/usr/bin/env python3

import socket

class POP3Server:
    def __init__(self, host='localhost', port=0):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((host, port))
        self.server_socket.listen(1)
        self.client_socket = None

        self.respdict = None

        # The POP3Server class is intended to be used in a 'log-based' testing
        # for client scripts. It buffers all the input passed by the client, 
        # so, after executing some test pattern, you can inspect the log and
        # check if the desired conditions were fulfilled.
        self.recvlog = []

    def accept(self):
        socket, address = self.server_socket.accept()
        self.client_socket = socket

    def exit(self):
        if self.client_socket:
            self.client_socket.close()
        self.server_socket.close()

    def set_respdict(self, respdict):
        self.respdict = respdict

    def get_conninfo(self):
        return self.server_socket.getsockname()

    def get_logiter(self):
        return (line for line in self.recvlog)

    def greeting(self):
        self.client_socket.send(self.respdict['greeting'])

    def recvline(self, eol=b'\r\n'):
        line = b''
        while True:
            bt = self.client_socket.recv(1)
            if not bt:
                break
            line += bt
            if line[-2:] == eol:
                break
        self.recvlog.append(line)
        return line

    def talkback(self, line):
        exit = False
        line = line.decode().rstrip()
        cmd = line.split(' ')[0].lower()
        self.client_socket.send(self.respdict[cmd])

        if cmd == 'quit':
            exit = True
        return exit

    # Running server
    def run(self):
        self.accept()
        self.greeting()
        while True:
            line = self.recvline()
            if not line or self.talkback(line):
                break
        self.exit()
