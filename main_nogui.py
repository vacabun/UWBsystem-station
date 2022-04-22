# -*- coding: utf-8 -*-

# Native python
import logging
import os
import sys

# package
import serial
import serial.tools.list_ports


import data_analyze

# debug log output
path = os.path.abspath(os.path.join(os.getcwd(), "../.."))
logging.basicConfig(level=logging.DEBUG,
                    filename=path + '/log.txt',
                    filemode='a',
                    format='%(asctime)s - %(levelname)s: %(message)s'
                    )

if __name__ == '__main__':
    portlist = list(serial.tools.list_ports.comports())
    if len(portlist) == 1:
        com = str(portlist[0]).split()[0]
        ser = serial.Serial(port = com, baudrate=1000000, bytesize=8, parity='N', stopbits=1, timeout=None)
        data_analyze = data_analyze.DataAnalyze()
        flag = ser.is_open
        if flag:
            print('Serial open success.')
            while True:
                char_rev = ser.read(1)
                data_analyze.analyze(char_rev[0])
        else:
            print('Serial open error.')
        sys.exit()
    else:
        print('No USB serial device or too much.')
        sys.exit()

