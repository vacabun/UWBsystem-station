# -*- coding: utf-8 -*-
import logging
import os
import time
import sys
import serial
import serial.tools.list_ports
import pandas
from process.network import SocketClient
from process.sql_helper import SqlHelper
from process.data_analyze import DataAnalyze
from process.data_process import process_measure_data
from process.config import load_config

# debug log output
logging.basicConfig(level=logging.DEBUG,
                    filename='log.txt',
                    filemode='a',
                    format='%(asctime)s - %(levelname)s: %(message)s'
                    )


def main_service(com, baud):
    # read data.
    data_analyze = DataAnalyze()
    sql_helper = SqlHelper()
    frame_num = 0
    config = load_config()
    ip = config['server_ip']
    port = config['server_port']
    sc = SocketClient(ip, port)
    while (True):
        test_c_list = [0x4d, 0x7b] + [82, 2, 3, 0, frame_num, 0, 37] + [0x7d]
        test_c_list += [0x4d, 0x7b] + [82, 2, 4, 0, frame_num, 0, 25] + [0x7d]
        test_c_list += [0x4d, 0x7b] + [82, 2, 5, 0, frame_num, 0, 26] + [0x7d]
        test_c_list += [0x4d, 0x7b] + [82, 2, 6, 0, frame_num, 0, 27] + [0x7d]
        frame_num = frame_num+1
        if frame_num == 125:
            frame_num = 0
        for c in test_c_list:
            if measure_data := data_analyze.analyze(c):
                sql_helper.add_data(measure_data)
                process_measure_data(measure_data, sc)
        test_c_list = [0x4d, 0x7b] + [82, 3, 3, 0, frame_num, 0, 137] + [0x7d]
        test_c_list += [0x4d, 0x7b] + [82, 3, 4, 0, frame_num, 0, 25] + [0x7d]
        test_c_list += [0x4d, 0x7b] + [82, 3, 5, 0, frame_num, 0, 26] + [0x7d]
        test_c_list += [0x4d, 0x7b] + [82, 3, 6, 0, frame_num, 0, 27] + [0x7d]
        frame_num = frame_num+1
        if frame_num == 125:
            frame_num = 0
        for c in test_c_list:
            if measure_data := data_analyze.analyze(c):
                sql_helper.add_data(measure_data)
                process_measure_data(measure_data, sc)
        time.sleep(2)


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

    com = str(portlist[0]).split()[0] if (
        len(portlist) == 1) else config['com']

    main_service(com, 1000000)

    sys.exit()
