import threading
import serial
import data_analyze


class ReadPort(threading.Thread):
    def __init__(self, thread_id, name, counter):
        threading.Thread.__init__(self)
        self.ser = None
        self.data_analyze = data_analyze.DataAnalyze()
        self.port_thread_flag = False

    def connect(self, port):
        self.ser = serial.Serial(port, baudrate=1000000, bytesize=8, parity='N', stopbits=1, timeout=None)
        self.port_thread_flag = True
        self.daemon = True
        self.start()

    def run(self):
        while True:
            if self.port_thread_flag:
                # test
                # str_send = 'hello\n'
                # self.ser.write(str_send.encode())
                # 接收串口数据并执行解析
                char_rev = self.ser.read(1)

                self.data_analyze.analyze(char_rev[0])
                # time.sleep(1)
            else:
                print('close port')
                break
