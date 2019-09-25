# -*- coding:utf-8 -*-

"""
 代码加载器（以模块的方式加载）
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
