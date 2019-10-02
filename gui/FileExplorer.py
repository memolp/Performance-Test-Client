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
    文件查看器
author:
    JeffXun
"""

import os

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

import gui.Config as Config

class VFileExplorer(QWidget):
    """"""
    file_open_event = pyqtSignal(str)
    def __init__(self, parent=None):
        """"""
        super(VFileExplorer, self).__init__(parent)
        self.setMinimumWidth(100)

        self.mFileList = QListWidget()
        self.mFileList.setObjectName("list-explorer")
        layout = QVBoxLayout(self)
        layout.addWidget(self.mFileList)
        self.setLayout(layout)
        self.mFileList.doubleClicked.connect(self.OnOpenSelFile)

        self.RefreshList()

    def RefreshList(self):
        """"""
        self.mFileList.clear()

        for filename in os.listdir(Config.PROJECT_TEST_PATH):
            self.mFileList.addItem(filename)

    def OnOpenSelFile(self,event):
        """
        双击打开文件
        :param event:
        :return:
        """
        basename = self.mFileList.currentItem().text()
        filename = os.path.join(Config.PROJECT_TEST_PATH,basename)
        if os.path.exists(filename):
            self.file_open_event.emit(filename)
