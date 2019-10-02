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
    界面GUI操作
author:
    JeffXun
"""

import os
import sys

from PyQt5.Qt import QApplication
from gui.RobotEditor import VRobotEditor

import gui.Config as Config

Config.PROJECT_PATH = os.path.dirname(__file__)
Config.PROJECT_TEST_PATH = os.path.join(Config.PROJECT_PATH,"script/")
Config.PROJECT_QSS_PATH = os.path.join(Config.PROJECT_PATH,"style.qss")
Config.PROJECT_PTC_CONFIG = os.path.join(Config.PROJECT_PATH,"config.properties")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    editor = VRobotEditor()
    editor.show()
    sys.exit(app.exec_())
