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
    查看用戶状态，也可以向用户发送信息
author:
    JeffXun
"""

import math
import ConsoleMain

from PyQt5.QtWidgets import *


class VUserStatusView(QDialog):
    """"""
    def __init__(self, parent, config):
        """"""
        super(VUserStatusView, self).__init__(parent)

        self.setWindowTitle("用户状态列表")
        self.setMinimumWidth(800)
        self.setMinimumHeight(600)
        _vLayout = QVBoxLayout()

        self.mVUserTable = QTableWidget()
        self.mVUserTable.setObjectName("table-user")
        _vLayout.addWidget(self.mVUserTable)

        _hLayout = QHBoxLayout()
        _btnRefresh = QPushButton("刷新")
        _btnRefresh.setObjectName('btn-refresh')
        _btnRefresh.clicked.connect(self.RefreshVusers)
        _hLayout.addStretch(1)
        _hLayout.addWidget(_btnRefresh)
        _vLayout.addLayout(_hLayout)

        self.setLayout(_vLayout)

        if config is None:
            return

        self.mRow = config['tps']
        self.mCol = math.ceil(config['user'] / config['tps'])
        self.mVUserTable.setRowCount(self.mRow)
        self.mVUserTable.setColumnCount(self.mCol)
        # 设置列宽
        for i in range(self.mRow):
            self.mVUserTable.setColumnWidth(i, 120)
        for i in range(self.mRow):
            for j in range(self.mCol):
                self.mVUserTable.setItem(i, j, QTableWidgetItem(""))

        self.RefreshVusers()

    def RefreshVusers(self):
        """"""
        user_list = ConsoleMain.GetRunUsers()
        size = len(user_list)
        for i in range(size):
            user = user_list[i]
            row = i % self.mRow
            col = int(i / self.mRow)
            status = "User_{0}({1})".format(i, user.GetStateLabel())
            item = self.mVUserTable.item(row, col)
            if item:
                item.setText(status)

