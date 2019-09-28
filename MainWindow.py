# -*- coding:utf-8 -*-

"""
  压测脚本编辑界面
"""

import sys

from PyQt5.Qt import QApplication
from gui.RobotEditor import VRobotEditor


if __name__ == "__main__":
    app = QApplication(sys.argv)
    editor = VRobotEditor()
    editor.show()
    sys.exit(app.exec_())
