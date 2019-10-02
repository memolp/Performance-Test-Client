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
    代码加载器（以模块的方式加载）
author:
    JeffXun
"""

import os
import sys
import importlib

class ModuleClass(type(sys)):
    """
    创建一个模块类
    """
    pass

def cimport(name):
    """"""
    importlib.import_module(name)

def LoadModule(filename):
    """
    加载模块
    :param filename:
    :return:
    """
    # 安全检查
    if not os.path.exists(filename):
        return None
    # 读取文件
    with open(filename,"rb") as pf:
        source = pf.read()
        pf.close()

    # 获取模块基础名
    mode_base_name = os.path.basename(filename)
    mode_name = mode_base_name[:mode_base_name.find('.')]

    # 创建模块
    mode = ModuleClass(filename)
    mode.__file__ = filename
    mode.__dict__.update({"import":cimport})

    # 编译模块
    code = compile(source, filename, "exec")
    exec(code, mode.__dict__, mode.__dict__)
    # 已加载模块的替换
    if mode_name in sys.modules:
        del sys.modules[mode_name]
    sys.modules[mode_name] = mode
    return mode
