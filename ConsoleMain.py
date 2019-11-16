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
    控制台入口
    压测脚本将支持GUI和控制台（方便可以在多平台下运行）
author:
    JeffXun
"""

import os
import sys
import math
import argparse

from core.net.VSocketMgr import VSocketMgr
from core.vuser.VUserMgr import VUserMgr
from core.utils import Loader
from core.utils import VLog


def Main():
    """
    入口
    :return:
    """
    try:
        parse = argparse.ArgumentParser(prog="PTClient-console")
        parse.add_argument("-host", help="PTC Server host", type=str)
        parse.add_argument("-port", help="PTC Server port", type=int)
        parse.add_argument("-user", help="User Count", type=int)
        parse.add_argument("-tps", help="translation per second", type=int)
        parse.add_argument("-index", help="User index", type=int, default=0)
        parse.add_argument("-times", help="run test times", type=int, default=-1)
        parse.add_argument("-initdelay", help="init user delay", type=float, default=0.1)
        parse.add_argument("-script", help="script file abspath", type=str)
        parse.add_argument("-thread_net", help="thread of network num", type=int, default=4)
        parse.add_argument("-thread_tps", help="thread of tps num", type=int, default=10)
        parse.add_argument("-recv_buff", help="network recv buffer size", type=int, default=1024*1024)
        parse.add_argument("-max_fd", help="select max fd num", type=int, default=500)
        # 解析
        argument = parse.parse_args()
        RunConsole(argument)
    except Exception as e:
        print(e)

def RunConsole(argument):
    """"""
    max_select_fd = math.ceil(argument.user / argument.max_fd)
    VSocketMgr.MAX_SELECT_TASK_NUM = argument.thread_net
    VSocketMgr.RECV_MAX_BUFF_SIZE = argument.recv_buff
    VSocketMgr.PTC_HOST = argument.host
    VSocketMgr.PTC_PORT = argument.port
    VUserMgr.RUN_TEST_TIMES = argument.times
    VUserMgr.MAX_THREAD_NUM = argument.thread_tps

    # 压测脚本
    script_file = argument.script
    if not os.path.exists(script_file):
        VLog.Error("[PTC] Test Script {0} not exist!",script_file)
        return
    # 添加压测脚本目录
    sys.path.append(os.path.dirname(__file__))
    # 加载压测脚本
    module = Loader.LoadModule(script_file)
    if module is None:
        VLog.Error("[PTC] Load Script {0} Error!", script_file)
        return
    # 网络线程组启动
    VSocketMgr.GetInstance().CreateServer(module, max_select_fd)
    # 用户管理启动
    VUserMgr.GetInstance().CreateVUser(module, argument.user, argument.tps, argument.index)
    VUserMgr.GetInstance().Start(argument.initdelay)
    StopConsole()

def GetRunUsers():
    """"""
    return VUserMgr.GetInstance().GetAllUsers()

def StopConsole():
    """"""
    VSocketMgr.GetInstance().Stop()
    VUserMgr.GetInstance().Stop()

def LocalTest():
    """
    本地测试代码
    :return:
    """
    VSocketMgr.MAX_SELECT_TASK_NUM = 5
    VSocketMgr.PTC_HOST = "127.0.0.1"
    VSocketMgr.PTC_PORT = 7090
    VUserMgr.RUN_TEST_TIMES = 900

    # 压测脚本
    script_file = "./script/test.py"
    # 添加压测脚本目录
    sys.path.append(os.path.dirname(__file__))
    # 加载压测脚本
    module = Loader.LoadModule(script_file)
    if module is None:
        return
    user = 10000
    tps  = 1000
    # 网络线程组启动
    VSocketMgr.GetInstance().CreateServer(module, 20)
    # 用户管理启动
    VUserMgr.GetInstance().CreateVUser(module, user, tps)
    VUserMgr.GetInstance().Start(0.3)
    StopConsole()

if __name__ == "__main__":
    if len(sys.argv) <= 1:
        LocalTest()
    else:
        Main()
