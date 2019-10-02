# -*- coding:utf-8 -*-

"""
 关于
"""

from PyQt5.QtWidgets import *
from PyQt5.Qt import *

class VAboutDialog(QDialog):
    """ 关于对话框 """
    def __init__(self,parent=None):
        """ """
        super(VAboutDialog,self).__init__(parent)
        self.setWindowTitle("关于")
        _vLayout = QVBoxLayout()
        _vLayout.addWidget(QLabel("压测工具\r\n作者:Jeff\r\n2019-09-30"))
        self.setLayout(_vLayout)