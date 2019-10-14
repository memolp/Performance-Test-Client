# -*- coding:utf-8 -*-

"""
MIT License

Copyright (c) 2019 JeffXun

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

content:
    进程监控
author:
    JeffXun
"""

import os
import psutil

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

import gui.Config as Config

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

        _gridLayout.addWidget(QLabel("离线压测进程："), 2, 1, 1, 3)
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
                if pinfo['name'].lower() == Config.PTC_CLIENT_PROCESS_NAME.lower():
                    self.mPTCClient.addItem("客户端:{0}".format(pinfo['pid']))
                elif pinfo['name'].lower() == "java.exe":
                    cmd = proc.cmdline()
                    if Config.PTC_CENTER_PROCESS_NAME in cmd:
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
            cmd = "java -jar {0}".format(Config.PTC_CENTER_PROCESS_NAME)
            result = os.popen(cmd)
            print(result)

    def __kill_pid(self,pid):
        find_kill = 'taskkill -f -pid %s' % pid
        result = os.system(find_kill)
        if result == 0:
            print("关闭进程成功")

    def _closeClient(self):
        """"""
        current_item = self.mPTCClient.currentItem()
        if current_item is None:
            return
        text = self.mPTCClient.currentItem().text()
        if text is None or len(text) <= 0:
            return
        pid_str = text[text.rfind(":")+1:]
        if pid_str and pid_str.isdecimal():
            self.__kill_pid(pid_str)

    def isPTCRunning(self):
        return self.mPTCRunning