# -*- coding: utf-8 -*-

# Native python
import logging
import os
import sys

# package
import serial
import serial.tools.list_ports
import json

import data_analyze

# debug log output
path = os.path.abspath(os.path.join(os.getcwd(), ".."))
logging.basicConfig(level=logging.DEBUG,
                    filename=path + '/log.txt',
                    filemode='a',
                    format='%(asctime)s - %(levelname)s: %(message)s'
                    )

if __name__ == '__main__':
    portlist = list(serial.tools.list_ports.comports())
    if len(portlist) > 0 :
        com = ''
        if(len(portlist) == 1):
            com = str(portlist[0]).split()[0]
        else:
            with open("./config.json", 'r') as load_f:
                config = json.load(load_f)

            com = config['com']
        ser = serial.Serial(port = com, baudrate=1000000, bytesize=8, parity='N', stopbits=1, timeout=None)
        data_analyze = data_analyze.DataAnalyze()
        if flag := ser.is_open:
            print('Serial open success.')
            while True:
                char_rev = ser.read(1)
                data_analyze.analyze(char_rev[0])
        else:
            print('Serial open error.')        
    else :
        print('No USB serial device.')

    sys.exit()

