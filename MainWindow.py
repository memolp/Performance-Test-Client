# -*- coding:utf-8 -*-

"""
  压测脚本编辑界面
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
