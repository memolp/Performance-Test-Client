# -*- coding:utf-8 -*-

"""
 文件查看器
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
