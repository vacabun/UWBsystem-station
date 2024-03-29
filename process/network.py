import socket
import string
import logging


class SocketClient:
    def __init__(self, sever_ip: string, sever_port: int):
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sever_ip = sever_ip
        self.sever_port = sever_port
        try:
            self.s.connect((self.sever_ip, self.sever_port))
        except socket.error as e:
            print(e)
        except Exception as e:
            logging.error(e)

    def send(self, msg: string):
        try:
            if not self.s.getpeername():
                self.s.connect((self.sever_ip, self.sever_port))
            if self.s.getpeername():
                self.s.send(msg.encode())
        except socket.error as e:
            print(e)
        except Exception as e:
            logging.error(e)
