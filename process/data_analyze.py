# -*- coding: utf-8 -*-
import json
import logging
import time
import socket
import csv

import process.network
from process.typedef import MeasureData
from process.filter import filter

debug_f = True


class DataAnalyze:
    def __init__(self):
        self.header = b'\x4d\x7b'
        self.ending = b'\x7d'
        self.escape = False
        self.headerCounter = 0
        self.endingCounter = 0
        self.counter = 0
        self.receive_data = []
        self.data = {}
        self.filterData = {}

    def _clean_receive(self):
        self.headerCounter = 0
        self.endingCounter = 0
        self.counter = 0
        self.receive_data = []

    def analyze(self, data: int):

        if data == 0xfe:
            self.escape = True
            return None
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
        if self.counter == 2:
            if self.receive_data[0] == 82 and len(self.receive_data) == 7:
                measure_data = self.package_measure_data()
                self._clean_receive()
                return measure_data
            else:
                self._clean_receive()
        return None

    def package_measure_data(self) -> MeasureData:
        label_address = self.receive_data[1]
        node_address = self.receive_data[2]
        frame_num = (self.receive_data[3] << 8) + self.receive_data[4]
        asctime = time.asctime()
        distance = (self.receive_data[5] << 8) + self.receive_data[6]
        res = MeasureData(label_address=label_address, node_address=node_address, frame_num=frame_num,
                          asctime=asctime, distance=distance)
        return res
