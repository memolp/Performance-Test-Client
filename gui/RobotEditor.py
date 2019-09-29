# -*- coding:utf-8 -*-

"""
  编辑器
  -----------------------------------------------------------------
   IDE                                                     - 口 X
  -----------------------------------------------------------------
  |                      菜单栏                                    |
  |                       工具栏                                   |
  -----------------------------------------------------------------
  |              |                                                |
  |              |                                                |
  |              |                                                |
  | dock         |         table widget view/ python editor       |
  | fileExplorer |                                                |
  |              |                                                |
  |              |                                                |
  |              |                                                |
  -----------------------------------------------------------------
  |                    dock console                               |
  |                                                               |
  -----------------------------------------------------------------
"""
import os
import win32process
import ConsoleMain

from PyQt5.QtWidgets import *
from PyQt5.Qt import *

from gui.FileExplorer import VFileExplorer
from gui.ScriptEditor import VScriptEditor
from gui.ConsoleView import VConsoleView
from gui.RunTestDialog import RunTestDialog
from core.utils.VTemplate import str_template


class VTestThread(QThread):
    """"""
    def __init__(self, config, parent=None):
        super(VTestThread, self).__init__(parent)
        self._config = config
    def run(self):
        """"""
        ConsoleMain.RunConsole(self._config)
        del self._config


class VRobotEditor(QMainWindow):
    def __init__(self):
        super(VRobotEditor,self).__init__()
        self.setWindowTitle("压测机器人编辑器")
        self.setMinimumSize(800, 600)

        self._create_system_menu()

        self._create_toolbar()

        self.vFileExplorer = None
        self.vConsoleView = None
        self.vScriptEditor = VScriptEditor(self)
        self.setCentralWidget(self.vScriptEditor)
        self._create_dock()

        self.__testThread = None

    def _create_system_menu(self):
        """
        系统菜单
        :return:
        """
        _menuBar  = QMenuBar(self)
        _filemenu = _menuBar.addMenu("文件")
        _new_script_ac = QAction("新建压测场景", self)
        _new_script_ac.setShortcut("Ctrl+N")
        _new_script_ac.triggered.connect(self.__newScriptEvent)
        _filemenu.addAction(_new_script_ac)

        _open_script_ac = QAction("打开压测场景", self)
        _open_script_ac.setShortcut("Ctrl+O")
        _open_script_ac.triggered.connect(self.__openScriptEvent)
        _filemenu.addAction(_open_script_ac)

        _save_script_ac = QAction("保存压测场景", self)
        _save_script_ac.setShortcut("Ctrl+S")
        _save_script_ac.triggered.connect(self.__saveScriptEvent)
        _filemenu.addAction(_save_script_ac)

        _exit_ac = QAction("退出", self)
        _exit_ac.setShortcut("Ctrl+Q")
        _exit_ac.triggered.connect(self.__exitEvent)
        _filemenu.addAction(_exit_ac)

        _testmenu = _menuBar.addMenu("压测")
        _start_test_ac = QAction("开始压测", self)
        _start_test_ac.setShortcut("F5")
        _start_test_ac.triggered.connect(self.__runTestEvent)
        _testmenu.addAction(_start_test_ac)

        _stop_test_ac = QAction("停止压测", self)
        _stop_test_ac.triggered.connect(self.__stopTestEvent)
        _testmenu.addAction(_stop_test_ac)

        _toolmenu = _menuBar.addMenu("工具")
        _setting_ac = QAction("设置", self)
        _toolmenu.addAction(_setting_ac)

        _theme_ac = QAction("主题编辑", self)
        _toolmenu.addAction(_theme_ac)

        _helpmenu = _menuBar.addMenu("帮助")
        _about_ac = QAction("关于", self)
        _helpmenu.addAction(_about_ac)

        _check_up_ac = QAction("检查更新", self)
        _helpmenu.addAction(_check_up_ac)

        self.setMenuBar(_menuBar)

    def _create_toolbar(self):
        """
        工具栏
        :return:
        """
        _toolbar = self.addToolBar("工具栏")
        _new_script_ac = QAction("新建压测场景", self)
        _new_script_ac.triggered.connect(self.__newScriptEvent)
        _toolbar.addAction(_new_script_ac)

        _open_script_ac = QAction("打开压测场景", self)
        _open_script_ac.triggered.connect(self.__openScriptEvent)
        _toolbar.addAction(_open_script_ac)

        _toolbar.addAction(QAction("运行压测场景", self))
        _toolbar.addAction(QAction("停止压测场景", self))

    def _create_dock(self):
        """
        创建dock窗口
        :return:
        """
        file_dock = QDockWidget("文件管理器", self)
        file_dock.setFeatures(QDockWidget.DockWidgetMovable)
        file_dock.setAllowedAreas(Qt.LeftDockWidgetArea)
        self.vFileExplorer = VFileExplorer()
        file_dock.setWidget(self.vFileExplorer)
        self.addDockWidget(Qt.LeftDockWidgetArea, file_dock)
        self.vFileExplorer.file_open_event.connect(self._on_open_file)

        console_dock = QDockWidget("控制台", self)
        console_dock.setFeatures(QDockWidget.DockWidgetMovable)
        console_dock.setAllowedAreas(Qt.BottomDockWidgetArea)
        self.vConsoleView = VConsoleView()
        console_dock.setWidget(self.vConsoleView)
        self.addDockWidget(Qt.BottomDockWidgetArea, console_dock)
        self.vConsoleView.AttachConsole()

    def __newScriptEvent(self):
        """"""
        _scriptfile = QFileDialog.getSaveFileName(self,
                                                  caption="新建脚本",
                                                  directory="./script",
                                                  filter="Python Files(*.py)")
        if _scriptfile is None or len(_scriptfile) < 1 or _scriptfile[0] == '':
            return
        filename = _scriptfile[0]
        try:
            with open(filename,"wb") as pf:
                pf.write(str_template.encode())
        except Exception as e:
            return QMessageBox.critical(self, "提示", "创建文件失败:{0}".format(e))
        self.vFileExplorer.RefreshList()
        self.vScriptEditor.OpenFile(filename)

    def __openScriptEvent(self):
        """"""
        _scriptfile = QFileDialog.getOpenFileName(self,
                                                  caption="打开脚本",
                                                  directory="./script",
                                                  filter="Python Files(*.py)")
        if _scriptfile is None or len(_scriptfile) < 1 or _scriptfile[0] == '':
            return
        filename = _scriptfile[0]
        if not os.path.exists(filename):
            return
        self._on_open_file(filename)

    def __saveScriptEvent(self):
        """"""
        if not self.vScriptEditor.SaveFile():
            return QMessageBox.critical(self, "提示", "保存文件失败")

    def __exitEvent(self):
        """"""
        self.close()

    def __runTestEvent(self):
        """"""
        test_script = self.vScriptEditor.GetCurrentScript()
        if test_script is None:
            return QMessageBox.information(self, "提示", "请先打开压测场景")
        if not test_script.endswith(".py"):
            return QMessageBox.information(self, "提示", "请选择压测脚本")
        # 打开配置窗口
        dlg = RunTestDialog(self, test_script)
        dlg.exec()
        if not dlg.IsTesting():
            return
        config = dlg.GetTestConfig()
        # 执行检查
        if config['mode'] == 1:
            str_cmd = ""
            for key,value in config.items():
                str_cmd += "-{0} {1} ".format(key,value)
            self.LaunchApp("./ConsoleMain.exe",str_cmd)
        else:
            if self.__testThread is not None and self.__testThread.isRunning():
                return QMessageBox.information(self, "提示", "压测运行中")
            self.__testThread = VTestThread(config)
            self.__testThread.start()

    def __stopTestEvent(self):
        if self.__testThread is None or not self.__testThread.isRunning():
            return QMessageBox.information(self, "提示", "压测已结束")
        self.__testThread.stop()

    def _on_open_file(self, filename):
        """"""
        if not self.vScriptEditor.OpenFile(filename):
            return QMessageBox.critical(self, "提示", "打开文件失败")

    def LaunchApp(self, app , args=''):
        app_file = app.replace("\\", "/")
        app_root = app_file[:app_file.rfind("/")]
        result = win32process.CreateProcess(app, args, None, None, 0,
                    win32process.CREATE_NO_WINDOW, None, app_root,
                    win32process.STARTUPINFO())
        if not result or len(result) < 4:
            return False