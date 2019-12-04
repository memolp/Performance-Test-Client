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
import time
import multiprocessing

from core.utils import Loader
from core.utils import VLog
from core.VUserConcurrence import VUserConcurrence
from core.VUserRPCClient import PTCRPCClient

# 多进程支持
multiprocessing.freeze_support()

def OnProcessTest(scene_cfg, process_index=0, process_queue=None):
    """
    进程测试
    :param scene_cfg: 压测配置
    :param process_index: 启动的进程序号 0 ，1 ，2
    :param process_queue: 进程通信的队列
    :return:
    """
    # 添加压测脚本的环境变量
    sys.path.append(os.path.dirname(__file__))
    # 压测的场景脚本列表
    test_scene_scripts = []
    if isinstance(scene_cfg['script'], list or tuple):
        for script_cfg in scene_cfg['script']:
            script_module = Loader.LoadModule(script_cfg['file'])
            if not script_module:
                VLog.Error("[PTC] Load script {0} Error!".format(script_cfg['file']))
                continue
            scene = {"script": script_module, "times": script_cfg['times'], "max_times": script_cfg['max_times']}
            test_scene_scripts.append(scene)
    else:
        script_module = Loader.LoadModule(scene_cfg['script'])
        if not script_module:
            VLog.Error("[PTC] Load script {0} Error!".format(scene_cfg['script']))
            return
        test_scene_scripts.append({"script": script_module, "times": scene_cfg['times'], "max_times": scene_cfg['times']})

    if len(test_scene_scripts) <= 0:
        return

    # 创建RPC客户端
    rpc_client = PTCRPCClient()
    rpc_client.connect_rpc_server(scene_cfg['host'], scene_cfg['port'])
    # 创建并发对象
    concurrence = VUserConcurrence(process_queue)
    concurrence.set_rpc_obj(rpc_client)
    concurrence.set_users(scene_cfg['user'], scene_cfg['index'] + process_index * scene_cfg['user'])
    concurrence.set_concurrence(scene_cfg['tps'], scene_cfg['thread_tps'])
    # 执行压测 - 主循环
    concurrence.run_multi_concurrence(scene_cfg['initdelay'], test_scene_scripts)
    # 压测完成 - 关闭压测
    concurrence.exit_concurrence()
    rpc_client.close_connect()

def RunConsole(argument):
    """"""
    # 压测脚本
    script_file = argument['script']
    if not os.path.exists(script_file):
        VLog.Error("[PTC] Test Script {0} not exist!",script_file)
        return
    argument['process'] = argument.get("process", 1)
    OnMultiTest(argument)


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

    OnMultiTest(scene_config)


def OnMultiTest(scene_config):
    """
    创建多进程压测
    :param scece_cfg:
    :return:
    """
    # 创建消息队列，并启动压测进程
    process_queue = multiprocessing.Queue()
    process_list = []
    for i in range(scene_config['process']):
        p = multiprocessing.Process(target=OnProcessTest, args=(scene_config, i, process_queue))
        p.start()
        process_list.append(p)

    # 压测事务统计打印
    TRANS_FORMAT = "[{0}] total:{1} finish:{2} response:{3}ms rate:{4}% tps:{5}"
    test_all_translations = {}
    while True:
        # 如果全部进程压测完成，则退出
        process_exit = True
        for process in process_list:
            if process.is_alive():
                process_exit = False
                break
        if process_exit:
            break

        if process_queue.empty():
            time.sleep(1)
            continue
        trans_msg = process_queue.get()
        if trans_msg is None:
            continue
        trans_info = eval(trans_msg)
        for mname in trans_info.keys():
            if mname not in test_all_translations:
                test_all_translations[mname] = trans_info[mname]
                test_all_translations['record'] = 1
            else:
                test_all_translations[mname]['total'] += trans_info[mname]['total']
                test_all_translations[mname]['finish'] += trans_info[mname]['finish']
                test_all_translations[mname]['response'] += trans_info[mname]['response']
                test_all_translations[mname]['record'] += 1
            total = test_all_translations[mname]['total']
            finish = test_all_translations[mname]['finish']
            rate = round(finish / total * 100, 2)
            response = round(test_all_translations[mname]['response'] / test_all_translations[mname]['record'], 2)
            tps = int(test_all_translations[mname]['finish'] / response * 1000)
            VLog.Info(TRANS_FORMAT.format(mname, total, finish, response, rate, tps))


def LocalTest():
    """
    本地测试代码
    :return:
    """
    scene_cfg = dict()
    scene_cfg['host'] = "127.0.0.1"
    scene_cfg['port'] = 7090
    scene_cfg['user'] = 500
    scene_cfg['tps'] = 50
    scene_cfg['thread_tps'] = 4
    scene_cfg['index'] = 0
    scene_cfg['initdelay'] = 0
    scene_cfg['times'] = 2
    scene_cfg['process'] = 2
    scene_cfg['script'] = "./script/test.py"

    VLog.PROFILE_OPEN = True
    VUserConcurrence.WAITING_TIME = 10

    RunConsole(scene_cfg)


if __name__ == "__main__":
    if len(sys.argv) > 1:
        MultiTest(sys.argv[1])
    else:
        LocalTest()
