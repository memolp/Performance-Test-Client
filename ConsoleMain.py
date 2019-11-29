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
import json
import argparse
import multiprocessing

from core.utils import Loader
from core.utils import VLog
from core.VUserConcurrence import VUserConcurrence
from core.VUserRPCClient import PTCRPCClient
from core.rpc.RPCClient import RPCConnectType


def Main():
    """
    入口
    :return:
    """
    try:
        parse = argparse.ArgumentParser(prog="PTC_Console")
        parse.add_argument("-host", help="RPC Server host", type=str)
        parse.add_argument("-port", help="RPC Server port", type=int)
        parse.add_argument("-user", help="User Count", type=int)
        parse.add_argument("-tps", help="translation per second", type=int)
        parse.add_argument("-index", help="User index", type=int, default=0)
        parse.add_argument("-times", help="run test times", type=int, default=-1)
        parse.add_argument("-initdelay", help="init user delay", type=float, default=0.1)
        parse.add_argument("-script", help="script file abspath", type=str)
        parse.add_argument("-thread_tps", help="thread of tps num", type=int, default=2)
        parse.add_argument("-recv_buff", help="network recv buffer size", type=int, default=1024*1024)
        # 解析
        argument = parse.parse_args()
        RunConsole(argument)
    except Exception as e:
        print(e)

def RunConsole(argument):
    """"""
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

    rpc_client = PTCRPCClient()
    rpc_client.connect_rpc_server(argument.host, argument.port, RPCConnectType.SOCK_TCP)
    concurrence = VUserConcurrence()
    concurrence.set_rpc_obj(rpc_client)
    concurrence.set_users(argument.user, argument.index)
    concurrence.set_concurrence(argument.tps, argument.thread_tps)
    concurrence.run_concurrence(module, argument.times, argument.initdelay)


def MultiTest(sence_cfg):
    """
    综合场景压测
    :param sence_cfg:
    :return:
    """
    if not os.path.exists(sence_cfg):
        VLog.Error("file {0} is not exist!", sence_cfg)
        return
    with open(sence_cfg, "rb") as pf:
        scene_config = json.load(pf)
    # 添加压测脚本目录
    sys.path.append(os.path.dirname(__file__))
    scenes = []
    for script in scene_config['scripts']:
        # 加载压测脚本
        module = Loader.LoadModule(script['file'])
        if module:
            scene = {"script":module, "times": script['times'], "max_times":script['max_times']}
            scenes.append(scene)

    rpc_client = PTCRPCClient()
    rpc_client.connect_rpc_server(scene_config['host'], scene_config['port'], RPCConnectType.SOCK_TCP)
    concurrence = VUserConcurrence()
    concurrence.set_rpc_obj(rpc_client)
    concurrence.set_users(scene_config['user'],scene_config['index'])
    concurrence.set_concurrence(scene_config['tps'], scene_config['thread_tps'])
    concurrence.run_multi_concurrence(scene_config['initdelay'], scenes)

def LocalTest():
    """
    本地测试代码
    :return:
    """
    # 压测脚本
    script_file = "./script/test.py"
    # 添加压测脚本目录
    sys.path.append(os.path.dirname(__file__))
    # 加载压测脚本
    module = Loader.LoadModule(script_file)
    if module is None:
        return

    user = 500
    tps = 100

    VLog.VLog.Performance_Log = True

    process = multiprocessing.Process()

    rpc_client = PTCRPCClient()
    rpc_client.connect_rpc_server("127.0.0.1", 7090, RPCConnectType.SOCK_TCP)
    concurrence = VUserConcurrence()
    concurrence.set_rpc_obj(rpc_client)
    concurrence.set_users(user)
    concurrence.set_concurrence(tps, 2)
    concurrence.run_concurrence(module, 3600)

    while True:
        sign = input("'q' to exit\n'p' to print translation\n>:")
        if sign == 'q':
            break
        elif sign == 'p':
            concurrence.display_translation()
    concurrence.exit_concurrence()


if __name__ == "__main__":
    if len(sys.argv) <= 1:
        LocalTest()
    elif len(sys.argv) <= 2:
        MultiTest(sys.argv[1])
    else:
        Main()
