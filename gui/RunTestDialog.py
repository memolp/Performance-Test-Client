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

        self.mTestScript = test_script
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

    _help_of_mode = """
    在线模式：
        即通过IDE运行压测客户端，由于对性能会产生影响，仅在调试或者少量用户时使用。
    离线模式：
        即在控制台运行压测客户端，可以提高压测客户端的性能，但有些功能将无法支持。
    """
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
        self.mTestModeCombox.setToolTip(self._help_of_mode)
        _gLayout.addWidget(self.mTestModeCombox, 2, 2)

        _gLayout.addWidget(QLabel("用户数量:"), 3, 1)
        self.mTestUserInput = QLineEdit("50")
        self.mTestUserInput.setObjectName("input-user")
        self.mTestUserInput.setToolTip("用户数量：即压测的用户总数，或者为在线用户总数")
        _gLayout.addWidget(self.mTestUserInput, 3, 2)

        _gLayout.addWidget(QLabel("并发TPS:"), 3, 3)
        self.mTestTpsInput = QLineEdit("1")
        self.mTestTpsInput.setObjectName("input-tps")
        self.mTestTpsInput.setToolTip("并发TPS：即尽量每秒有多少用户执行指定的事物行为(尽量在于每秒是否有足够的用户可以参与并发)")
        _gLayout.addWidget(self.mTestTpsInput, 3, 4)

        _gLayout.addWidget(QLabel("压测轮次:"), 4, 1)
        self.mTestRoundInput = QLineEdit("-1")
        self.mTestRoundInput.setObjectName("input-round")
        self.mTestRoundInput.setToolTip("压测轮次：即执行多少次并发，在每秒并发前提下也就是压测的时间")
        _gLayout.addWidget(self.mTestRoundInput, 4, 2)

        _gLayout.addWidget(QLabel("用户初始化间隔:"), 4, 3)
        self.mUserInitDelayInput = QLineEdit("0.0")
        self.mUserInitDelayInput.setObjectName("input-init-delay")
        self.mUserInitDelayInput.setToolTip("设置用户初始化的时间间隔，初始化以并发数进行")
        _gLayout.addWidget(self.mUserInitDelayInput, 4, 4)

        _normalWidget.setLayout(_gLayout)
        return _normalWidget

    def _create_detail_options(self):
        """"""
        _details_widget = QWidget()
        _gLayout = QGridLayout()

        _gLayout.addWidget(QLabel("PTC服务IP:"), 1, 1)
        self.mTestPTCHostInput = QLineEdit("127.0.0.1")
        self.mTestPTCHostInput.setObjectName('input-host')
        self.mTestPTCHostInput.setToolTip("压测高并发网络服务IP，即PerformanceController.jar程序的地址")
        _gLayout.addWidget(self.mTestPTCHostInput, 1, 2)
        _gLayout.addWidget(QLabel("PTC服务端口:"), 1, 3)
        self.mTestPTCPortInput = QLineEdit("7090")
        self.mTestPTCPortInput.setObjectName('input-port')
        self.mTestPTCPortInput.setToolTip("压测高并发网络服务端口，即PerformanceController.jar程序的端口")
        _gLayout.addWidget(self.mTestPTCPortInput, 1, 4)

        _gLayout.addWidget(QLabel("线程用户数:"), 2, 1)
        self.mTestThreadFDNumInput = QLineEdit("500")
        self.mTestThreadFDNumInput.setObjectName('input-thread-fd')
        self.mTestThreadFDNumInput.setToolTip("由于select有socket数量限制，此配置用于指定限制的数量")
        _gLayout.addWidget(self.mTestThreadFDNumInput, 2, 2)

        _gLayout.addWidget(QLabel("网络线程数:"), 3, 1)
        self.mTestNetThreadNumInput = QLineEdit("{0}".format(os.cpu_count()))
        self.mTestNetThreadNumInput.setObjectName('input-thread-net')
        self.mTestNetThreadNumInput.setToolTip("定义网络线程池的数量，执行网络数据接收(默认为CPU核数)")
        _gLayout.addWidget(self.mTestNetThreadNumInput, 3, 2)

        _gLayout.addWidget(QLabel("网络Buffer:"), 3, 3)
        self.mTestNetworkBuffInput = QLineEdit("{0}".format(1024*1024))
        self.mTestNetworkBuffInput.setObjectName("input-buff-net")
        self.mTestNetworkBuffInput.setToolTip("定义网络buff缓存大小，过小会有丢数据的风险")
        _gLayout.addWidget(self.mTestNetworkBuffInput, 3, 4)

        _gLayout.addWidget(QLabel("并发线程数:"), 4, 1)
        self.mTestTpsThreadNumInput = QLineEdit("{0}".format(os.cpu_count()))
        self.mTestTpsThreadNumInput.setObjectName('input-tps-net')
        self.mTestTpsThreadNumInput.setToolTip("定义并发线程池的数量，执行用户并发(默认为CPU核数)")
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
        config['script'] = self.mTestScript
        config['index'] = 0
        config['initdelay'] = float(self.__get_ele_text(self.mUserInitDelayInput, "0.0"))
        config['thread_net'] = int(self.__get_ele_text(self.mTestNetThreadNumInput, "4"))
        config['max_fd'] = int(self.__get_ele_text(self.mTestThreadFDNumInput, "500"))
        config['thread_tps'] = int(self.__get_ele_text(self.mTestTpsThreadNumInput, "10"))
        config['mode'] = 0
        config['sock_buff'] = int(self.__get_ele_text(self.mTestNetworkBuffInput, "102400"))
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