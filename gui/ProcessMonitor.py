# -*- coding:utf-8 -*-

"""
   进程监控
"""

import os
import psutil

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

PTC_CLIENT_PROCESS_NAME = "ConsoleMain.exe"
PTC_CENTER_PROCESS_NAME = "PerformanceController.jar"

class VProcessMonitor(QWidget):
    """"""
    def __init__(self, parent=None):
        """"""
        super(VProcessMonitor, self).__init__(parent)

        _gridLayout = QGridLayout()
        _gridLayout.addWidget(QLabel("PTC中心:"), 1, 1)
        self.mPTCProcess = QLabel("未启动")
        self.mPTCProcess.setObjectName("label-ptc")
        _gridLayout.addWidget(self.mPTCProcess, 1, 2)
        self.mPTCControl = QPushButton("启动")
        self.mPTCControl.setObjectName("btn-start")
        self.mPTCControl.clicked.connect(self.__btnPTCControl)
        _gridLayout.addWidget(self.mPTCControl, 1, 3)

        _gridLayout.addWidget(QLabel("压测进程："), 2, 1, 1, 3)
        self.mPTCClient = QListWidget()
        self.mPTCClient.setObjectName("list-client")
        self.mPTCClient.setContextMenuPolicy(Qt.CustomContextMenu);
        self.mPTCClient.customContextMenuRequested.connect(self.__rightMenuShow)
        _gridLayout.addWidget(self.mPTCClient, 3, 1, 1, 3)

        self.setLayout(_gridLayout)

        self.mTimer = QTimer()
        self.mTimer.setInterval(1000)
        self.mTimer.timeout.connect(self._freshProcessInfo)
        self.mTimer.start()

        self.mPTCRunning = False
        self.mPTCControlList = []

    # 创建右键菜单
    def __rightMenuShow(self):
        rightMenu = QMenu(self.mPTCClient)
        removeAction = QAction(u"关闭客户端", self, triggered=self._closeClient)
        rightMenu.addAction(removeAction)
        rightMenu.exec_(QCursor.pos())

    def _freshProcessInfo(self):
        """"""
        self.mPTCControlList = []
        self.mPTCClient.clear()
        for proc in psutil.process_iter():
            try:
                pinfo = proc.as_dict(attrs=['pid', 'name'])
                if pinfo['name'].lower() == PTC_CLIENT_PROCESS_NAME.lower():
                    self.mPTCClient.addItem("客户端:{0}".format(pinfo['pid']))
                elif pinfo['name'].lower() == "java.exe":
                    cmd = proc.cmdline()
                    if PTC_CENTER_PROCESS_NAME in cmd:
                        self.mPTCRunning = True
                        self.mPTCProcess.setText("已启动:{0}".format(pinfo['pid']))
                        self.mPTCControl.setText("停止")
                        self.mPTCControl.setObjectName("btn-stop")
                        self.mPTCControlList.append(pinfo['pid'])
            except psutil.NoSuchProcess:
                pass
        if not self.mPTCRunning:
            self.mPTCProcess.setText("未启动")

    def __btnPTCControl(self):
        """"""
        if self.mPTCRunning:
            for pid in self.mPTCControlList:
                self.__kill_pid(pid)

            self.mPTCControl.setText("启动")
            self.mPTCControl.setObjectName("btn-start")
            self.mPTCRunning = False
        else:
            cmd = "java -jar {0}".format(PTC_CENTER_PROCESS_NAME)
            result = os.popen(cmd)
            print(result)

    def __kill_pid(self,pid):
        find_kill = 'taskkill -f -pid %s' % pid
        result = os.system(find_kill)
        if result == 0:
            print("关闭进程成功")

    def _closeClient(self):
        """"""
        text = self.mPTCClient.currentItem().text()
        pid_str = text[text.rfind(":")+1:]
        if pid_str and pid_str.isdecimal():
            self.__kill_pid(pid_str)

    def isPTCRunning(self):
        return self.mPTCRunning