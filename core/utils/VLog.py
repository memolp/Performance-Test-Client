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


class _interl_cls:
    """日志等级"""
    level = 0

class VLog:
    """日志"""
    level = 0

    @staticmethod
    def setLevel(level):
        """
        设置日志等级
        :param level:
        :return:
        """
        VLog.level = level

    @staticmethod
    def Debug(fmt, *args):
        """
        debug日志
        :param fmt:
        :param args:
        :return:
        """
        if VLog.level <= 0:
            sLog = fmt.format(*args)
            print("{0} [DEBUG] {1}".format(round(time.time(), 3), sLog))

    @staticmethod
    def Info(fmt, *args):
        """
        info日志
        :param fmt:
        :param args:
        :return:
        """
        if VLog.level <= 1:
            sLog = fmt.format(*args)
            print("{0} [INFO] {1}".format(round(time.time(), 3), sLog))

    @staticmethod
    def Warning(fmt, *args):
        """
        warning日志
        :param fmt:
        :param args:
        :return:
        """
        if VLog.level <= 2:
            sLog = fmt.format(*args)
            print("{0} [INFO] {1}".format(round(time.time(), 3), sLog))

    @staticmethod
    def Error(fmt, *args):
        """
        error 日志打印
        :param fmt:
        :param args:
        :return:
        """
        if VLog.level <= 3:
            sLog = fmt.format(*args)
            print("{0} [ERROR] {1}".format(round(time.time(), 3), sLog))

    @staticmethod
    def Fatal(fmt, *args):
        """
        Fatal日志
        :param fmt:
        :param args:
        :return:
        """
        if VLog.level <= 4:
            sLog = fmt.format(*args)
            print("{0} [ERROR] {1}".format(round(time.time(), 3), sLog))

    @staticmethod
    def Trace(msg):
        """
        打印堆栈
        :return:
        """
        print("{0} [TRACE] {1} stack: {2}".format(round(time.time(), 3), msg, traceback.format_exc()))

def setLevel(level):
    """
    设置日志等级
    :param level:
    :return:
    """
    VLog.setLevel(level)


def Debug(fmt, *args):
    """
    debug 日志打印
    :param fmt: {0} {1} 格式
    :param args:
    :return:
    """
    VLog.Debug(fmt, *args)


def Info(fmt, *args):
    """
    info日志
    :param fmt:
    :param args:
    :return:
    """
    VLog.Info(fmt, *args)


def Warning(fmt, *args):
    """
    warning日志
    :param fmt:
    :param args:
    :return:
    """
    VLog.Warning(fmt, *args)


def Error(fmt, *args):
    """
    error 日志打印
    :param fmt:
    :param args:
    :return:
    """
    VLog.Error(fmt, *args)


def Fatal(fmt, *args):
    """
    Fatal日志
    :param fmt:
    :param args:
    :return:
    """
    VLog.Fatal(fmt, *args)


def Trace(msg):
    """
    打印堆栈
    :return:
    """
    VLog.Trace(msg)
