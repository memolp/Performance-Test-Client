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
    运行设置
author:
    JeffXun
"""

import os

from PyQt5.QtWidgets import *
from PyQt5.Qt import *

from core.utils.VAttrObject import VAttrObject

class RunTestDialog(QDialog):
    """ 运行测试选择对话框 """
    def __init__(self,parent, test_script):
        """ """
        super(RunTestDialog,self).__init__(parent)
        self.setWindowTitle("运行设置")
        self.setFixedWidth(400)
        self.setFixedHeight(240)

        self.mNomalWidget = self._create_test_options(os.path.basename(test_script))
        self.mDetailsWidget = self._create_detail_options()
        self.mBtnsWidget = self._create_btns()

        _vLayout = QVBoxLayout()
        _vLayout.addWidget(self.mNomalWidget)
        _vLayout.addWidget(self.mDetailsWidget)
        _vLayout.addWidget(self.mBtnsWidget)
        self.setLayout(_vLayout)

        self.mDetailsWidget.setVisible(False)

        self.mTestFlag = False

    def _create_test_options(self,test_script_name):
        """"""
        _normalWidget = QWidget()
        _gLayout = QGridLayout()

        _gLayout.addWidget(QLabel("压测场景:"), 1, 1)
        self.mTestScriptLabel = QLabel(test_script_name)
        _gLayout.addWidget(self.mTestScriptLabel, 1, 2)

        _gLayout.addWidget(QLabel("运行模式:"), 2, 1)
        self.mTestModeCombox = QComboBox()
        self.mTestModeCombox.setObjectName("combox-mode")
        self.mTestModeCombox.addItems(["在线模式", "离线模式"])
        _gLayout.addWidget(self.mTestModeCombox, 2, 2)

        _gLayout.addWidget(QLabel("用户数量:"), 3, 1)
        self.mTestUserInput = QLineEdit("50")
        self.mTestUserInput.setObjectName("input-user")
        _gLayout.addWidget(self.mTestUserInput, 3, 2)

        _gLayout.addWidget(QLabel("压测轮次:"), 4, 1)
        self.mTestRoundInput = QLineEdit("-1")
        self.mTestRoundInput.setObjectName("input-round")
        _gLayout.addWidget(self.mTestRoundInput, 4, 2)

        _gLayout.addWidget(QLabel("并发TPS:"), 5, 1)
        self.mTestTpsInput = QLineEdit("1")
        self.mTestTpsInput.setObjectName("input-tps")
        _gLayout.addWidget(self.mTestTpsInput, 5, 2)

        _normalWidget.setLayout(_gLayout)
        return _normalWidget

    def _create_detail_options(self):
        """"""
        _details_widget = QWidget()
        _gLayout = QGridLayout()

        _gLayout.addWidget(QLabel("PTC服务IP:"), 1, 1)
        self.mTestPTCHostInput = QLineEdit("127.0.0.1")
        self.mTestPTCHostInput.setObjectName('input-host')
        _gLayout.addWidget(self.mTestPTCHostInput, 1, 2)
        _gLayout.addWidget(QLabel("PTC服务端口:"), 1, 3)
        self.mTestPTCPortInput = QLineEdit("7090")
        self.mTestPTCPortInput.setObjectName('input-port')
        _gLayout.addWidget(self.mTestPTCPortInput, 1, 4)

        _gLayout.addWidget(QLabel("线程用户数:"), 2, 1)
        self.mTestThreadFDNumInput = QLineEdit("500")
        self.mTestThreadFDNumInput.setObjectName('input-thread-fd')
        _gLayout.addWidget(self.mTestThreadFDNumInput, 2, 2)

        _gLayout.addWidget(QLabel("网络线程数:"), 3, 1)
        self.mTestNetThreadNumInput = QLineEdit("{0}".format(os.cpu_count()))
        self.mTestNetThreadNumInput.setObjectName('input-thread-net')
        _gLayout.addWidget(self.mTestNetThreadNumInput, 3, 2)

        _gLayout.addWidget(QLabel("并发线程数:"), 4, 1)
        self.mTestTpsThreadNumInput = QLineEdit("{0}".format(os.cpu_count()))
        self.mTestTpsThreadNumInput.setObjectName('input-tps-net')
        _gLayout.addWidget(self.mTestTpsThreadNumInput, 4, 2)

        _details_widget.setLayout(_gLayout)
        return _details_widget

    def _create_btns(self):
        """"""
        _btn_widget = QWidget()
        _hLayout = QHBoxLayout()

        _hLayout.addStretch(1)
        self.mBtnTest = QPushButton("开始")
        self.mBtnTest.setObjectName('btn-run')
        self.mBtnTest.clicked.connect(self._readyToStart)
        _hLayout.addWidget(self.mBtnTest)

        self.mBtnDetails = QPushButton("高级")
        self.mBtnDetails.setObjectName('btn-details')
        self.mBtnDetails.clicked.connect(self.__toggle_details_layout)
        _hLayout.addWidget(self.mBtnDetails)

        self.mBtnCancel = QPushButton("取消")
        self.mBtnCancel.setObjectName('btn-cancel')
        self.mBtnCancel.clicked.connect(self.__close)
        _hLayout.addWidget(self.mBtnCancel)

        _btn_widget.setLayout(_hLayout)
        return _btn_widget

    def __toggle_details_layout(self):
        """ """
        text = self.mBtnDetails.text()
        if text == "高级":
            self.mDetailsWidget.setVisible(True)
            self.setFixedWidth(400)
            self.setFixedHeight(360)
            self.mBtnDetails.setText("简单")
        else:
            self.mDetailsWidget.setVisible(False)
            self.setFixedWidth(400)
            self.setFixedHeight(240)
            self.mBtnDetails.setText("高级")

    def __get_ele_text(self, ele, default=""):
        """"""
        text = ele.text()
        if len(text) <= 0:
            return default
        return text

    def GetTestConfig(self):
        """"""
        config = VAttrObject()
        config["host"] = self.__get_ele_text(self.mTestPTCHostInput, "127.0.0.1")
        config["port"] = int(self.__get_ele_text(self.mTestPTCPortInput, "7090"))
        config['user'] = int(self.__get_ele_text(self.mTestUserInput, "0"))
        config['tps'] = int(self.__get_ele_text(self.mTestTpsInput, "0"))
        config['times'] = int(self.__get_ele_text(self.mTestRoundInput,"-1"))
        config['script'] = self.__get_ele_text(self.mTestScriptLabel, None)
        config['thread_net'] = int(self.__get_ele_text(self.mTestNetThreadNumInput, "4"))
        config['max_fd'] = int(self.__get_ele_text(self.mTestThreadFDNumInput, "500"))
        config['thread_tps'] = int(self.__get_ele_text(self.mTestTpsThreadNumInput, "10"))
        config['mode'] = 0
        if self.mTestModeCombox.currentText() == "离线模式":
            config['mode'] = 1
        return config

    def __close(self):
        """"""
        self.mTestFlag = False
        self.close()

    def _readyToStart(self):
        """"""
        self.mTestFlag = True
        self.close()

    def IsTesting(self):
        return self.mTestFlag