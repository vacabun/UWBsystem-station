# -*- coding: utf-8 -*-

# Native python
import logging
import sys
import threading
import queue
import time

# package
import serial
import serial.tools.list_ports

from process.config import load_config
from process.sql_helper import SqlHelper
from process.data_analyze import DataAnalyze
from process.data_process import process_measure_data
from process.network import SocketClient
from process.config import load_config


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
    sql_helper = SqlHelper()

    config = load_config()
    ip = config['server_ip']
    port = config['server_port']
    sc = SocketClient(ip, port)

    # 启动一个线程来读取队列数据
    q = queue.Queue()
    thread = threading.Thread(target=process_from_queue, args=(q, sql_helper, sc))
    thread.start()

    while True:
        try:
            rev = ser.read()
            for c in rev:
                if measure_data := data_analyze.analyze(c):
                    q.put(measure_data)
        except Exception as e:
            print(e)
            logging.error(e)


def process_from_queue(q, sql_helper, sc):
    while True:
        while not q.empty():
            try:
                measure_data = q.get()
                sql_helper.add_data(measure_data)
                process_measure_data(measure_data, sc)
            except Exception as e:
                print(e)
                logging.error(e)
        time.sleep(0.1)


if __name__ == '__main__':
    # load config file.
    config = load_config()

    # load port.
    portlist = list(serial.tools.list_ports.comports())
    for port in portlist:
        print(str(port))
    if len(portlist) <= 0:
        logging.error('No USB serial device.')

    com = str(portlist[0]).split()[0] if (len(portlist) == 1) else config['com']

    main_service(com, 115200)

    sys.exit()
