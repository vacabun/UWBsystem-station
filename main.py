# -*- coding: utf-8 -*-

# Native python
import logging
import os
import sys

# package
import serial
import serial.tools.list_ports
import json
import pandas

from process.data_analyze import DataAnalyze

# debug log output
logging.basicConfig(level=logging.DEBUG,
                    filename='log.txt',
                    filemode='a',
                    format='%(asctime)s - %(levelname)s: %(message)s'
                    )


def main_service(com, baud):
    # open serial.
    ser = serial.Serial(port=com, baudrate=baud, bytesize=8,
                        parity='N', stopbits=1, timeout=None)

    if ser.is_open:
        logging.info('Serial open success.')
    else:
        logging.error('Serial open error.')
        sys.exit()

    # # read data.
    data_analyze = DataAnalyze()

    while (True):
        try:
            rev = ser.read_all()
            for c in rev:
                data_analyze.analyze(c)
            # char_rev = ser.read(1)
            # data_analyze.analyze(char_rev[0])

        except Exception as e:
            logging.error(e)


def load_config():
    df = pandas.read_excel('config/config.xlsx')
    return df.loc[0, ['server_ip', 'server_port', 'com', ]].to_dict()


if __name__ == '__main__':

    # load config file.
    config = load_config()

    # load port.
    portlist = list(serial.tools.list_ports.comports())
    if len(portlist) <= 0:
        logging.error('No USB serial device.')

    com = str(portlist[0]).split()[0] if (len(portlist) == 1) else config['com']

    main_service(com, 1000000)

    sys.exit()
