import socket
import string
import sys


class SocketClient:
    def __init__(self, sever_ip: string, sever_port: int):
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sever_ip = sever_ip
        self.sever_port = sever_port

    def send(self, msg: string):
        try:
            self.s.connect((self.sever_ip, self.sever_port))
            self.s.send(msg.encode())
            self.s.close()
        except socket.error as msg:
            print(msg)
