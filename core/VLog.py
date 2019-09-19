# -*- coding:utf-8 -*-

"""
 日志打印
"""

import time
import traceback

DEBUG = False

def Debug(fmt , *args):
    """
    debug 日志打印
    :param fmt: {0} {1} 格式
    :param args:
    :return:
    """
    if DEBUG:
        sLog = fmt.format(*args)
        print("{0} [DEBUG] {1}".format(round(time.time(), 3), sLog))

def Info(fmt, *args):
    """
    info日志
    :param fmt:
    :param args:
    :return:
    """
    sLog = fmt.format(*args)
    print("{0} [INFO] {1}".format(round(time.time(), 3), sLog))

def Error(fmt, *args):
    """
    error 日志打印
    :param fmt:
    :param args:
    :return:
    """
    sLog = fmt.format(*args)
    print("{0} [ERROR] {1}".format(round(time.time(), 3), sLog))

def Trace(msg):
    """
    打印堆栈
    :return:
    """
    print("{0} [TRACE] {1} stack: {2}".format(round(time.time(), 3),msg, traceback.format_exc()))
