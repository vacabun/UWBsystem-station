# -*- coding: utf-8 -*-
import json
import logging
import time

import location
import measure_data
import sql_helper
import network


class DataAnalyze:
    def __init__(self):
        self.header = b'\x4d\x7b'
        self.ending = b'\x7d'
        self.headerCounter = 0
        self.endingCounter = 0
        self.counter = 0
        self.receive_data = []
        self.data = {}
        self.escape = False

    def _clean_receive(self):
        self.headerCounter = 0
        self.endingCounter = 0
        self.counter = 0
        self.receive_data = []

    def analyze(self, data):
        if data == 0xfe:
            self.escape = True
            return
        if self.escape:
            if data == 0xFD:
                data = 0xFF
            elif data == 0xFC:
                data = 0xFE
            self.escape = False
        # header
        if self.counter == 0:
            if self.header[self.headerCounter] == data:
                self.headerCounter = self.headerCounter + 1
                if self.headerCounter >= len(self.header):
                    self.counter = self.counter + 1
        # data
        elif self.counter == 1:
            if self.ending[self.endingCounter] == data:
                self.endingCounter = self.endingCounter + 1
                if self.endingCounter >= len(self.ending):
                    self.counter = self.counter + 1
            else:
                self.receive_data.append(data)
        # end
        elif self.counter == 2:
            self._process()
            self._clean_receive()

    def _process(self):
        if self.receive_data[0] == 82:
            if len(self.receive_data) == 7:
                self.process_measure_data()

    def process_measure_data(self):
        res = self._analyze_measure_data()

        print('{asctime}:\t{label_address}\t<--->\t{node_address}\t[{frame_num}]:\t{distance}'.format(
            asctime=res.asctime, label_address=res.label_address, node_address=res.node_address,
            frame_num=res.frame_num, distance=res.distance))
        logging.debug('{asctime}:\t{label_address}\t<--->\t{node_address}\t[{frame_num}]:\t{distance}'.format(
            asctime=res.asctime, label_address=res.label_address, node_address=res.node_address,
            frame_num=res.frame_num, distance=res.distance))

        helper = sql_helper.SqlHelper()
        helper.add_data(res)

        if not res.label_address in self.data.keys():
            self.data[res.label_address] = []
        elif self.data[res.label_address][0].frame_num != res.frame_num:
            if len(self.data[res.label_address]) < 4:
                print('label' + str(res.label_address) + '   packet loss')
            self.data[res.label_address] = []

        self.data[res.label_address].append(res)

        if len(self.data[res.label_address]) >= 4:
            [x, y] = self._cal_location_4(res.label_address, self._get_near_4_address(res.label_address))
            print([res.label_address, x, y, len(self.data[res.label_address])])

            msg = '\"asctime\": \"{asctime}\",\"frame_num\": \"{frame_num}\",\"label_address\": \"{label_address}\",' \
                  '\"x\": \"{x}\",\"y\": \"{y}\"'.format(asctime=time.asctime(), frame_num=res.frame_num,
                                                         label_address=res.label_address, x=x, y=y)
            msg = '{' + msg + '}'
            # print(msg)
            sc = network.SocketClient("192.168.31.127", 7999)
            sc.send(msg)

    def _cal_location_4(self, label_address: int, node_address_4: [int, int, int, int]) -> [int, int]:
        loca = location.Location()

        datas = self.data[label_address]

        distance = [0, 0, 0, 0]
        for i in range(4):
            for j in range(len(datas)):
                if datas[i].node_address == node_address_4[i]:
                    distance[i] = datas[i].distance / 100
                    break
        loca.set_distances(distance)

        with open("./anthor.json", 'r') as load_f:
            anthors = json.load(load_f)
        anthor_4 = []
        for i in range(4):
            for anthor in anthors:
                if anthor['address'] == node_address_4[i]:
                    anthor_4.append([anthor['x'], anthor['y'], anthor['z']])
                    break
        loca.set_anthor_coor(anthor_4)

        return loca.trilateration_4()

    def _get_near_4_address(self, label_address: int) -> [int, int, int, int]:
        datas = self.data[label_address]
        d = [0xfff, 0xfff, 0xfff, 0xfff]
        address = [0, 0, 0, 0]
        index = 0
        for i in range(4):
            for j in range(i, len(datas)):
                if datas[j].distance < d[i]:
                    d[i] = datas[j].distance
                    address[i] = datas[j].node_address
                    index = j
            datas[index], datas[i] = datas[i], datas[index]
        return address

    def _analyze_measure_data(self) -> measure_data.MeasureData:
        label_address = self.receive_data[1]
        node_address = self.receive_data[2]
        frame_num = (self.receive_data[3] << 8) + self.receive_data[4]
        asctime = time.asctime()
        distance = (self.receive_data[5] << 8) + self.receive_data[6]
        res = measure_data.MeasureData(label_address=label_address, node_address=node_address, frame_num=frame_num,
                                       asctime=asctime, distance=distance)
        return res
