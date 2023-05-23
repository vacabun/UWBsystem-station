# -*- coding: utf-8 -*-
import json
import logging
import time
import socket
import csv

import location
import typedef
import sql_helper
import network
from filter import filter

debug_f = True


class DataAnalyze:
    def __init__(self):
        self.header = b'\x4d\x7b'
        self.ending = b'\x7d'
        self.headerCounter = 0
        self.endingCounter = 0
        self.counter = 0
        self.receive_data = []
        self.data = {}
        self.filterData = {}
        self.escape = False

    def _clean_receive(self):
        self.headerCounter = 0
        self.endingCounter = 0
        self.counter = 0
        self.receive_data = []

    def analyze(self, data: int):
        
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
                self._process_measure_data()

    def _analyze_measure_data(self) -> typedef.MeasureData:
        label_address = self.receive_data[1]
        node_address = self.receive_data[2]
        frame_num = (self.receive_data[3] << 8) + self.receive_data[4]
        asctime = time.asctime()
        distance = (self.receive_data[5] << 8) + self.receive_data[6]
        res = typedef.MeasureData(label_address=label_address, node_address=node_address, frame_num=frame_num,
                                       asctime=asctime, distance=distance)
        return res

    def _process_measure_data(self):
        res = self._analyze_measure_data()
        data = self.data
        filterData = self.filterData
        label_address = res.label_address
        node_address = res.node_address
        distance = res.distance

        # debug log out
        if debug_f:
            print('{asctime}:\t{label_address}\t<--->\t{node_address}\t[{frame_num}]:\t{distance}'.format(
                asctime=res.asctime, label_address=res.label_address, node_address=res.node_address,
                frame_num=res.frame_num, distance=res.distance))
            logging.debug('{asctime}:\t{label_address}\t<--->\t{node_address}\t[{frame_num}]:\t{distance}'.format(
                asctime=res.asctime, label_address=res.label_address, node_address=res.node_address,
                frame_num=res.frame_num, distance=res.distance))

        # sql
        helper = sql_helper.SqlHelper()
        helper.add_data(res)

        if not label_address in filterData.keys():
            filterData[label_address] = {}

        if not label_address in filterData[label_address].keys():
            filterData[label_address][node_address] = []

        filterData[label_address][node_address].append(distance)

        _, filterdistance = filter(filterData[label_address][node_address])

        print('[filter] {asctime}:\t{label_address}\t<--->\t{node_address}\t[{frame_num}]:\t{filterdistance}'.format(
            asctime=res.asctime, label_address=res.label_address, node_address=res.node_address,
            frame_num=res.frame_num, filterdistance=filterdistance))

        # new label join
        if not label_address in data.keys():
            data[label_address] = []

        # new frame
        elif self.data[label_address][0].frame_num != res.frame_num:
            # packet loss
            if len(self.data[label_address]) < 4:
                if debug_f:
                    print('label {label_address} packet loss'.format(
                        label_address=label_address))
            # clean res data list
            data[label_address] = []

        data[label_address].append(res)

        if len(self.data[res.label_address]) >= 4:
            self._cal_location(res.label_address)

    def _cal_location(self, label_address: int):
        # node_cal = self._get_near_4_address(res.label_address)
        data = self.data
        frame_num = data[label_address][0].frame_num
        node_cal = self._get_group_4_address(label_address)

        if not node_cal == [0, 0, 0, 0]:
            [x, y] = self._cal_location_4(label_address, node_cal)

            print([label_address, x, y, len(self.data[label_address])])

            with open("log/res.csv", mode="w", encoding="utf-8-sig", newline="") as f:
                writer = csv.writer(f)
                writer.writerow(
                    [time.asctime(), frame_num, label_address, x, y])

            with open("./config.json", 'r') as load_f:
                config = json.load(load_f)

            ip = config['sever_ip']
            port = config['sever_port']

            try:
                msg = '\"asctime\": \"{asctime}\",\"frame_num\": \"{frame_num}\",\"label_address\": \"{label_address}\",' \
                    '\"x\": \"{x}\",\"y\": \"{y}\"'.format(asctime=time.asctime(), frame_num=frame_num,
                                                           label_address=label_address, x=x, y=y)
                msg = '{' + msg + '}'
                logging.debug(msg)
                sc = network.SocketClient(ip, port)
                sc.send(msg)
            except socket.error as err:
                print(err)

    def _cal_location_4(self, label_address: int, node_address_4: [int, int, int, int]) -> [int, int]:
        loca = location.Location()

        datas = self.data[label_address]

        distance = [0, 0, 0, 0]
        for i in range(4):
            for j in range(len(datas)):
                if datas[j].node_address == node_address_4[i]:
                    distance[i] = datas[j].distance / 100
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

    def _get_group_4_address(self, label_address: int) -> [int, int, int, int]:
        datas = self.data[label_address]

        address = [0, 0, 0, 0]

        with open("./group.json", 'r') as load_f:
            rooms = json.load(load_f)

        res_address = []
        for i in range(len(datas)):
            res_address.append(datas[i].node_address)

        room_vote = {}

        for i in range(len(rooms)):
            room_vote[rooms[i]['roomId']] = []
            for j in range(len(rooms[i]['nodeId'])):
                if rooms[i]['nodeId'][j] in res_address:
                    room_vote[rooms[i]['roomId']].append(rooms[i]['nodeId'][j])

        for k in room_vote.keys():
            if len(room_vote[k]) >= 4:
                return room_vote[k][0:4]

        return address
