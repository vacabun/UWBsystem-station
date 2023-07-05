import socket
import string
import sys


class SocketClient:
    def __init__(self, sever_ip: string, sever_port: int):
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sever_ip = sever_ip
        self.sever_port = sever_port
        try:
            self.s.connect((self.sever_ip, self.sever_port))
        except socket.error as msg:
            print(msg)
        except Exception as e:
            logging.error(e)
    def send(self, msg: string):
        try:
            if self.s.getpeername():
                self.s.send(msg.encode())
            else:
                self.s.connect((self.sever_ip, self.sever_port))
        except socket.error as msg:
            print(msg)
        except Exception as e:
            logging.error(e)
