# -*- coding: utf-8 -*-

import os
import sys

from PySide6 import QtCore
from PySide6 import QtWidgets

import serial
import serial.tools.list_ports


import read_port


class MainWindow(QtWidgets.QWidget):

    def __init__(self):
        super().__init__()

        # 大小
        self.main_window_height = 600
        self.main_window_width = 600
        # 定义布局
        self.main_hbox = QtWidgets.QHBoxLayout(self)
        self.info_vbox = QtWidgets.QVBoxLayout(self)
        # 定义控件
        self.map = QtWidgets.QGraphicsView(self)
        self.uartInfoLabel = QtWidgets.QLabel(self)
        self.uartPortComboBox = QtWidgets.QComboBox(self)
        self.uartConnectBtn = QtWidgets.QPushButton(self)
        self.scene = QtWidgets.QGraphicsScene(self)

        self.portThread = None
        self.portList = None

        self.initUI()

    def initUI(self):

        # 调整窗口大小
        self.resize(self.main_window_width, self.main_window_height)
        self.setMaximumSize(self.main_window_width, self.main_window_height)
        self.setMinimumSize(self.main_window_width, self.main_window_height)
        # 地图
        self.map.setScene(self.scene)
        self.map.resize(int(self.main_window_width / 10 * 4), int(self.main_window_height / 10 * 4))
        self.map.setStyleSheet("padding: 0px; border: 0px;")  # 内边距和边界去除
        self.map.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignTop)  # 改变对齐方式
        self.map.setSceneRect(0, 0, self.map.viewport().width(), self.map.height())  # 设置图形场景大小和图形视图大小一致
        self.map.setObjectName("map")

        # 串口
        self.portList = list(serial.tools.list_ports.comports())
        self.uartInfoLabel.setText("串口")
        if len(self.portList) == 0:
            self.uartInfoLabel.setText("未监测到串口")
        else:
            self.uartInfoLabel.setText(" 监测到串口 ")
            for port in self.portList:
                self.uartPortComboBox.addItem(str(port.device))
        self.uartConnectBtn.setText('连接')
        self.uartConnectBtn.setCheckable(True)
        self.uartConnectBtn.clicked[bool].connect(self.connectPort)

        self.portThread = read_port.ReadPort(1, "Thread-readPort", 1)

        # 设置布局
        self.setLayout(self.main_hbox)
        self.main_hbox.addWidget(self.map)
        self.main_hbox.addLayout(self.info_vbox)
        self.info_vbox.addWidget(self.uartInfoLabel)
        self.info_vbox.addWidget(self.uartPortComboBox)
        self.info_vbox.addWidget(self.uartConnectBtn)

        self.setWindowTitle('UWB')
        self.show()

    def connectPort(self, pressed):
        source = self.sender()
        if source.text() == '连接':
            # 连接串口
            if self.uartPortComboBox.currentText() != '':
                self.portThread.connect(self.uartPortComboBox.currentText())
                self.uartConnectBtn.setText('已连接')
            else:
                QtWidgets.QMessageBox.warning(self, '警告', '请选择正确的端口', QtWidgets.QMessageBox.Yes, QtWidgets.QMessageBox.Yes)
        elif source.text() == '已连接':
            # 断开连接
            self.portThread.portThreadFlag = False
            self.uartConnectBtn.setText('连接')

    # 关闭程序
    def closeEvent(self, event):
        event.accept()
        os._exit()
