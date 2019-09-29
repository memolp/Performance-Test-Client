# -*- coding:utf-8 -*-

"""
 脚本编辑器
"""

import os

from PyQt5.Qt import *
from PyQt5.QtWidgets import *
from PyQt5.Qsci import *


class VScriptView(QsciScintilla):
    """"""
    text_changed = pyqtSignal(str)
    def __init__(self, basename, parent=None):
        """"""
        QsciScintilla.__init__(self,parent)
        # 以\n换行
        self.setEolMode(self.SC_EOL_LF)
        # 自动换行。self.WrapWord是父类QsciScintilla的
        self.setWrapMode(self.WrapWord)
        # 自动补全。对于所有Ascii字符
        self.setAutoCompletionSource(self.AcsAll)
        # 自动补全大小写敏感
        self.setAutoCompletionCaseSensitivity(False)
        # 输入多少个字符才弹出补全提示
        self.setAutoCompletionThreshold(1)
        # 代码可折叠
        self.setFolding(True)
        # 设置默认字体
        self.setFont(QFont('Courier New', 12))

        # 0~4。第0个左边栏显示行号
        self.setMarginType(0, self.NumberMargin)
        # 我也不知道
        # self.setMarginLineNumbers(0, True)
        # 边栏背景颜色
        self.setMarginsBackgroundColor(QColor(120, 220, 180))
        # 边栏宽度
        self.setMarginWidth(0, 30)
        # 换行后自动缩进
        self.setAutoIndent(True)
        # 支持中文字符
        self.setUtf8(True)

        self.mNeedSaved = False

        self.mFilename = basename

    def setPythonScriptLexer(self):
        """"""
        self.mTextLexer = QsciLexerPython()
        self.setLexer(self.mTextLexer)

    def setTextLexer(self):
        """"""
        self.mTextLexer = QsciLexerTeX()
        self.setLexer(self.mTextLexer)

    def setTextChanged(self):
        """"""
        self.textChanged.connect(self._on_text_changed)

    def _on_text_changed(self):
        """"""
        self.mNeedSaved = True
        self.textChanged.disconnect(self._on_text_changed)
        #self.textChanged.dis
        print("_on_text_changed")
        self.text_changed.emit(self.mFilename)

    def SaveToFile(self, filename):
        """"""
        try:
            with open(filename,"wb") as pf:
                _text = self.text()
                pf.write(_text.encode())
        except Exception as e:
            print(e)
        self.textChanged.connect(self._on_text_changed)


class VScriptEditor(QTabWidget):
    """
    脚本编辑器 支持多页签显示，支持语法高亮
    """
    def __init__(self, parent=None):
        """
        创建脚本编辑器
        :param parent:
        """
        super(VScriptEditor, self).__init__(parent)
        self.setMinimumWidth(600)
        self.setMinimumHeight(500)
        self._cacheTabList = {}

    def OpenFile(self, filename):
        """
        打开文件，如果是py文件，自动调用py语法，否则为文本
        :param filename:
        :return:
        """
        # 设置到tab上面
        basename = os.path.basename(filename)
        cache_tab = self._cacheTabList.get(basename,None)
        if cache_tab is not None:
            self.setCurrentIndex(cache_tab["index"])
            return True
        textEditor = VScriptView(basename)
        # 设置语法
        if filename.endswith(".py"):
            textEditor.setPythonScriptLexer()
        else:
            textEditor.setTextLexer()
        try:
            # 传进来文件时需要检查文件存在
            with open(filename,'rb') as pf:
                for line in pf:
                    textEditor.append(line.decode())
        except Exception as e:
            return False
        # 添加页签并选中
        index = self.addTab(textEditor, basename)
        self.setCurrentIndex(index)
        self._cacheTabList[basename] = {"filename":filename,"index":index,"save":1}
        textEditor.text_changed.connect(self._on_text_changed)
        textEditor.setTextChanged()
        return True

    def SaveFile(self):
        editor = self.currentWidget()
        if editor is None:
            return False
        basename = editor.mFilename
        cache_tab = self._cacheTabList.get(basename, None)
        if cache_tab is None:
            return False
        if cache_tab['save'] == 1:
            return False
        editor.SaveToFile(cache_tab['filename'])
        cache_tab['save'] = 1
        self.setTabText(cache_tab['index'], "{0}".format(basename))
        return True

    def _on_text_changed(self, basename):
        """ """
        cache_tab = self._cacheTabList.get(basename,None)
        if cache_tab is not None:
            self.setTabText(cache_tab['index'],"{0} - 未保存".format(basename))
            cache_tab['save'] = 0

    def GetCurrentScript(self):
        """ """
        index = self.currentIndex()
        if index < 0:
            return None
        text = self.tabText(index)
        cache_tab = self._cacheTabList.get(text, None)
        if cache_tab is None:
            return None
        return cache_tab["filename"]
