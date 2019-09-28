# -*- coding:utf-8 -*-

"""
   控制台
"""

from PyQt5.QtWidgets import *


class VConsoleView(QWidget):
    """"""
    def __init__(self, parent=None):
        """"""
        super(VConsoleView, self).__init__(parent)
        self.setMinimumHeight(120)

        self.mConsole = QTextEdit()
        layout = QVBoxLayout(self)
        layout.addWidget(self.mConsole)
        self.setLayout(layout)