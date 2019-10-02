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
    控制台
author:
    JeffXun
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
        self.mConsole.setObjectName("edit-console")
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