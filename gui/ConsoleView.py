# -*- coding:utf-8 -*-

"""
   控制台
"""

import sys

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.Qt import *


class EmittingStream(QObject):
    textWritten = pyqtSignal(str)  # 定义一个发送str的信号
    def write(self, text):
        self.textWritten.emit(str(text))

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

        self._stdout_bk = sys.stdout
        self._stderr_bk = sys.stderr

    def AttachConsole(self):
        """"""
        sys.stdout = EmittingStream(textWritten=self.outputWritten)
        sys.stderr = EmittingStream(textWritten=self.outputWritten)

    def DetachConsole(self):
        """"""
        sys.stdout = self._stdout_bk
        sys.stderr = self._stderr_bk

    def outputWritten(self, text):
        cursor = self.mConsole.textCursor()
        cursor.movePosition(QTextCursor.End)
        cursor.insertText(text)
        self.mConsole.setTextCursor(cursor)
        self.mConsole.ensureCursorVisible()