#!/usr/bin/env python3

import socket

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
