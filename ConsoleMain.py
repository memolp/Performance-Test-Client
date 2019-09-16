# -*- coding:utf-8 -*-

"""
  控制台入口
  压测脚本将支持GUI和控制台（方便可以在多平台下运行）
"""

import argparse

from core.VSocketMgr import VSocketMgr
from core.VUserMgr import VUserMgr
from core import Loader

def Main():
    """
    入口
    :return:
    """
    parse = argparse.ArgumentParser(prog="PTClient-console")
    parse.add_argument("-host", help="PTC Server host", type=str)
    parse.add_argument("-port", help="PTC Server port", type=int)
    parse.add_argument("-user", help="User Count", type=int)
    parse.add_argument("-tps", help="translation per second", type=int)
    parse.add_argument("-script", help="script file abspath", type=int)
    parse.add_argument("-thread", help="thread of network num", type=int, default=4)
    parse.add_argument("-platform", help="platform system win or linux", type=str, default="win")
    # 解析
    argument = parse.parse_args()
    VSocketMgr.WIN_MAX_THREAD_NUM = argument.NUM
    VSocketMgr.PTC_HOST = argument.host
    VSocketMgr.PTC_PORT = argument.port

    module = Loader.LoadModule(argument.script)
    if module is None:
        return
    # 网络线程组启动
    VSocketMgr.GetInstance().CreateServer(module, argument.platform)
    # 用户管理启动
    VUserMgr.GetInstance().CreateVUser(module, argument.user, argument.tps)
    VUserMgr.GetInstance().Start()

def LocalTest():
    """
    本地测试代码
    :return:
    """
    VSocketMgr.WIN_MAX_THREAD_NUM = 4
    VSocketMgr.PTC_HOST = "127.0.0.1"
    VSocketMgr.PTC_PORT = 7090

    module = Loader.LoadModule("./script/test.py")
    if module is None:
        return
    # 网络线程组启动
    VSocketMgr.GetInstance().CreateServer(module, "win")
    # 用户管理启动
    VUserMgr.GetInstance().CreateVUser(module, 3, 1)
    VUserMgr.GetInstance().Start()

if __name__ == "__main__":
    LocalTest()
