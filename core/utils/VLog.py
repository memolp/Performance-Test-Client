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
    日志打印
author:
    JeffXun
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
